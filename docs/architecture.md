# Architecture

## Overview

CardioSense AI is a full-stack healthcare AI application for ECG **signal** and **image** analysis:

- **Frontend**: React + Vite + Tailwind CSS + React Router + Framer Motion + Plotly/Recharts
- **Backend**: FastAPI + SQLAlchemy + PyTorch + ReportLab
- **Database**: SQLite (local) / PostgreSQL (production)
- **Signal model**: Real trained PyTorch ECGCNN checkpoint (`ptbxl_cnn_best.pt`)
- **Image model**: Real trained PyTorch EfficientNet-B0 checkpoint (`models/image/best_model.pt`)

The two pipelines are fully independent: separate loaders, checkpoints, preprocessing, and predict
paths. They share the database, statistics, and UI.

## Data Flow (Signal)

```
Browser ── HTTP ──> FastAPI (uvicorn :8000)
                        │
                        ├─ POST /api/ecg/analyze
                        │     ├─ validate files (type, size, leads, fs, length)
                        │     ├─ read WFDB/.mat/.csv/.npy signal
                        │     ├─ preprocess (bandpass 0.5–40Hz, per-record z-score)
                        │     ├─ ECGCNN inference → probabilities
                        │     ├─ threshold → prediction + confidence
                        │     ├─ signal quality + statistics
                        │     ├─ Integrated Gradients explainability (non-NORM)
                        │     └─ save ECGAnalysis row (analysis_type="signal")
                        ├─ GET /api/ecg/history (paged, filtered, type filter)
                        ├─ GET /api/statistics (aggregates from DB)
                        ├─ GET /api/model/info (from model_config.json)
                        └─ GET /api/ecg/report/{id} (PDF via ReportLab)
```

## Data Flow (Image)

```
Browser ── HTTP ──> FastAPI (uvicorn :8000)
                        │
                        ├─ POST /api/ecg-image/analyze
                        │     ├─ validate file (ext/mime/size ≤ 20MB, decodability)
                        │     ├─ training-compatible transforms
                        │     │   (Resize 244 → CenterCrop 224 → ToTensor → ImageNet normalize)
                        │     ├─ EfficientNet-B0 inference → softmax (15 classes)
                        │     ├─ prediction = argmax, confidence, probabilities
                        │     ├─ real Grad-CAM overlay (hooks model.features[-1])
                        │     │   └─ failure ⇒ gradcam_available=false (save anyway)
                        │     ├─ save uploaded image + saved gradcam
                        │     └─ save ECGAnalysis row (analysis_type="image")
                        ├─ GET /api/ecg-image/{id} /image /gradcam
                        ├─ GET /api/ecg-image/report/{id} (PDF via ReportLab)
                        └─ POST /api/ecg-image/{id}/summary /assistant
```

## Directory Structure

```
backend/
├── app/
│   ├── main.py               FastAPI app + lifespan (loads both models once)
│   ├── api/                  health, ecg, ecg-image, history, statistics, model routes
│   ├── ml/                   model.py, predictor.py, preprocessing.py, explainability.py
│   │                         image_model.py, image_predictor.py, image_gradcam.py
│   ├── database/             database.py, models.py (SQLAlchemy), schemas.py (Pydantic)
│   ├── services/             ecg_service.py, image_service.py,
│   │                         report_service.py, summary_service.py
│   └── core/                 config.py (env), logging.py
├── config/model_config.json  real signal model config (classes, thresholds, shapes)
├── models/ptbxl_cnn_best.pt  signal checkpoint
├── models/image/             image checkpoint + model_config.json
├── uploads/                  uploaded files (ecg_images/, ecg_gradcams/, signals/)
├── reports/                  generated PDFs
└── tests/                    pytest suite

frontend/
├── src/
│   ├── components/           layout, dashboard, ecg (chart), results, assistant,
│   │                         analysis (type selector), image-analysis (uploader, gradcam)
│   ├── pages/                Landing, Dashboard, AnalyzeECG, Results, History, ...
│   ├── services/api.js       fetch wrapper (signal + image methods)
│   ├── hooks/, utils/, context/
│   ├── App.jsx               routes
│   └── main.jsx, index.css
├── public/favicon.svg
├── index.html, vite.config.js, tailwind.config.js
```

## Model Integration

Each model is loaded **once** at startup:

- Signal: `app/ml/model.py::ModelLoader` → `SIGNAL_MODEL_PATH` env var.
- Image: `app/ml/image_model.py::ImageModelLoader` → `IMAGE_MODEL_PATH` / `IMAGE_MODEL_CONFIG`
  env vars. A load failure (or `ENABLE_IMAGE_MODEL=false`) only affects the image pipeline.

Both use CUDA when available, otherwise CPU. Preprocessing reuses the original pipelines — the
image transforms come from `ecg-image-model/src/transforms.py` (Resize 244 → CenterCrop 224 →
ImageNet normalize), never reinvented.

## Explainability

- **Signal**: `app/ml/explainability.py` uses **Integrated Gradients** (a gradient-based method that
  fits the CNN). Attention maps are NOT used because the checkpoint is CNN-only — no Transformer
  exists. Output: lead-importance and time-importance.
- **Image**: `app/ml/image_gradcam.py` implements **Grad-CAM** (hooks on `model.features[-1]`),
  mirroring `ecg-image-model/src/gradcam.py`. Output: heatmap overlay.

Both degrade gracefully instead of fabricating attribution.

## AI Summary / Assistant

`app/services/summary_service.py` builds plain-language summaries and answers questions using **only**
data from the analysis record (prediction, confidence, probabilities, statistics) — branch-aware of
signal vs image analyses. It never diagnoses.

## Database

`ecg_analyses` rows carry `analysis_type` (`signal`/`image`), `model_name`, `image_path`,
`gradcam_path`, `gradcam_available`. `_migrate_sqlite()` upgrades existing databases in place.

## Key Design Rules

- No fake predictions, metrics, Grad-CAM, or hardcoded statistics.
- Signal thresholds come from `model_config.json`; image config from `models/image/model_config.json`.
- The two models never merge, average, or influence each other.
- Errors are logged in detail server-side, shown friendly to users.
- Medical disclaimer displayed in-app and on every report (image reports carry an image-specific one).
