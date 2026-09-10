<div align="center">

# 🫀 CardioSense AI

### *Intelligent ECG Analysis. Clearer Cardiac Insights.*

**A full-stack healthcare AI platform that analyzes ECG signals and ECG images using two real, already-trained PyTorch deep learning models — no fabricated predictions, metrics, or statistics, ever.**

[FastAPI](https://fastapi.tiangolo.com) · [PyTorch](https://pytorch.org) · [React](https://react.dev) · [Vite](https://vitejs.dev) · [Tailwind CSS](https://tailwindcss.com) · [SQLAlchemy](https://www.sqlalchemy.org) · [ReportLab](https://www.reportlab.com)

```
⚠️ Educational / research tool. NOT a medical diagnosis. See the Medical Disclaimer below.
```

</div>

---

## 📖 Table of Contents

- [What Is It?](#-what-is-it)
- [✨ Key Features](#-key-features)
- [🧠 The Two Real Models](#-the-two-real-models)
- [🧩 ECG Image Pattern Assessment](#-ecg-image-pattern-assessment)
- [🏗 Architecture](#-architecture)
- [📂 Repository Structure](#-repository-structure)
- [🚀 Getting Started](#-getting-started)
- [⚙ Configuration](#-configuration)
- [🐳 Docker](#-docker)
- [🖥 Using the App](#-using-the-app)
- [🔌 API Overview](#-api-overview)
- [🧪 Testing](#-testing)
- [🛠 Troubleshooting](#-troubleshooting)
- [🔒 Security](#-security)
- [🌍 Deployment](#-deployment)
- [⚠️ Medical Disclaimer](#️-medical-disclaimer)
- [📄 License](#-license)

---

## 💡 What Is It?

CardioSense AI is a complete **ECG analysis web application** built for research, learning, and
decision support. Users upload **ECG signals** (12-lead recordings) **or ECG images** (screenshots or
photo-readings of a paper ECG) and the app returns real model predictions, probabilities,
explainability, PDF reports, and plain-language summaries.

The two analysis pipelines are **fully independent** — they share the UI, database, and statistics,
but never interact at the model level:

| | ECG **Signal** | ECG **Image** |
|---|---|---|
| Input | WFDB `.hea`+`.dat`, `.mat`, `.csv`, `.npy`, `.txt` | PNG, JPG, JPEG (≤ 20 MB) |
| Model | 1-D CNN (ECGCNN) on PTB-XL | EfficientNet-B0 (transfer-learned, 15 classes) |
| Output | 5-class multi-label (NORM, MI, STTC, CD, HYP) | 15-beat-subclass softmax |
| Explainability | Integrated Gradients (lead + time) | Grad-CAM heatmap overlay |
| Report | Signal PDF report | Image PDF report + pattern assessment |

> 🎯 **Design principle:** Predictions come **only** from the real loaded checkpoints. Nothing is
> hardcoded, randomized, or fabricated — probabilities, confidence, statistics, gradient attributions,
> and Grad-CAM maps are all computed live from the actual trained weights.

---

## ✨ Key Features

**Signal analysis**
- Upload 12-lead ECGs in multiple formats (WFDB, MAT, CSV, NPY, TXT)
- Real multi-label inference with per-class thresholds from the model config
- Interactive waveform viewer (zoom / pan / reset / hover / lead selector)
- Integrated Gradients explainability with lead & time importance
- Signal statistics (amplitude, duration, quality, sampling rate)

**Image analysis**
- Upload an ECG image with instant preview + validation (type, size, decodability)
- Real EfficientNet-B0 inference → exact 15-class probabilities, confidence, argmax prediction
- **Real Grad-CAM** heatmap overlay (graceful degradation if it fails)
- Human-readable subclass labels, ECG group aggregation, and dynamic recommendations
- Pattern assessment with confidence & limitations and safety guidance

**Workspace & UX**
- Unified signal/image mode selector, shared results, history, dashboard, analytics
- Searchable, filterable, sortable history with type filter and pagination
- Live analytics dashboard computed from the database (signal + image breakdowns)
- CardioSense **Assistant** — answers questions using only in-app analysis data
- PDF report generation for both signal and image analyses
- Dark mode, responsive, accessible, motion-enhanced UI

---

## 🧠 The Two Real Models

Both models are loaded **once at application startup** and used as-is. They are **not retrained,
modified, or reimplemented** — the integration code reuses the original pipelines.

### 1️⃣ ECG Signal Model — ECGCNN

| Property | Value |
|---|---|
| Checkpoint | `backend/models/ptbxl_cnn_best.pt` |
| Architecture | 1-D CNN (4 conv blocks, ~339K params), **no** Transformer/attention |
| Input | `(12, 1000)` — 12 leads × 1000 samples @ 100 Hz (10 s) |
| Output | 5 logits → sigmoid, per-class thresholds (multi-label) |
| Classes | `NORM, MI, STTC, CD, HYP` |
| Preprocessing | Butterworth bandpass (0.5–40 Hz, order 4) + per-record z-score |
| Explainability | **Integrated Gradients** (lead_importance, time_importance) |

### 2️⃣ ECG Image Model — EfficientNet-B0

| Property | Value |
|---|---|
| Checkpoint | `backend/models/image/best_model.pt` |
| Architecture | torchvision `efficientnet_b0(weights=None)`, classifier → `Linear(…, 15)` |
| Input | RGB → Resize 244 → CenterCrop 224 → ImageNet normalize |
| Output | 15-class softmax; prediction = argmax |
| Classes | `A E F J L N Q R S V aa e f j p` (see pattern assessment table below) |
| Preprocessing | Reuses `ecg-image-model/src/transforms.py` (training-compatible, untouched) |
| Explainability | **Grad-CAM** on `model.features[-1]` |

> 📚 Both integrate with the real metric/config data (`backend/config/model_config.json` and
> `backend/models/image/model_config.json`). See [`MODEL_INTEGRATION.md`](MODEL_INTEGRATION.md).

---

## 🧩 ECG Image Pattern Assessment

On top of the raw 15-class output, the app derives a deterministic, human-readable pattern
assessment — **no extra model, no retraining** — implemented in
`backend/app/ml/image_interpretation.py`.

**All 15 subclasses (human-readable labels):**

| Code | Subclass | ECG Group |
|---|---|---|
| `N` | Normal Beat | Normal |
| `L` | Left Bundle Branch Block Beat | Normal |
| `R` | Right Bundle Branch Block Beat | Normal |
| `e` | Atrial Escape Beat | Normal |
| `j` | Junctional Escape Beat | Normal |
| `A` | Atrial Premature Beat | Supraventricular |
| `J` | Junctional Premature Beat | Supraventricular |
| `S` | Supraventricular Premature Beat | Supraventricular |
| `aa` | Aberrated Atrial Premature Beat | Supraventricular |
| `V` | Ventricular Premature Beat (PVC) | Ventricular |
| `E` | Ventricular Escape Beat | Ventricular |
| `F` | Fusion Beat | Fusion |
| `Q` | Unclassifiable Beat | Other/Unclassifiable |
| `p` | Paced Beat | Other/Unclassifiable |
| `f` | Fusion/Paced Beat | Other/Unclassifiable |

**What happens per analysis (web + PDF, from the same data):**

1. **Predicted class** — shown as the human-readable subclass (e.g. "*Unclassifiable Beat*").
2. **All 15 subclass probabilities** — sorted highest → lowest, exact model percentages, human labels
   only (raw codes stay internal).
3. **ECG Pattern Group Summary** — five aggregated group probabilities (sums of member subclasses):
   Normal = `N+L+R+e+j`, Supraventricular = `A+J+S+aa`, Ventricular = `V+E`, Fusion = `F`,
   Other/Unclassifiable = `Q+p+f`.
4. **ECG Pattern Report** — interpretation based on the *complete* distribution (dominant pattern,
   strongest group, confidence assessment, abnormal-pattern note, professional-review flag).
5. **Recommended Next Steps** — generated **dynamically from the actual predicted subclass**, never
   from a hardcoded example. Includes an uncertainty note when confidence is low or probabilities are
   spread, and an emergency-safety notice. It never prescribes medication or treatment.
6. **Confidence & Limitations** + **Medical disclaimer**.

> Raw class codes are stored in the backend but **never displayed** as user-facing predictions or
> probability labels on the web page or PDF.

---

## 🏗 Architecture

```
Browser ── HTTP ──> FastAPI (uvicorn :8000)
                        ├─ /api/ecg/*          signal pipeline
                        ├─ /api/ecg-image/*    image pipeline
                        ├─ /api/history        paged + filtered history
                        ├─ /api/statistics     live aggregations
                        ├─ /api/model/*        model info / status
                        └─ SQLite / PostgreSQL storage
```

- **Frontend** — React 18 + Vite 6 + Tailwind CSS 3 + React Router + Framer Motion + Plotly/Recharts.
- **Backend** — FastAPI + SQLAlchemy 2 + PyTorch + ReportLab.
- **DB** — SQLite by default, PostgreSQL for production. `_migrate_sqlite()` upgrades existing DBs
  in place (old records are preserved and re-enriched on read).

See [`docs/architecture.md`](docs/architecture.md) for data-flow diagrams and design rules.

---

## 📂 Repository Structure

```
cardiosense-ai/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI entrypoint (loads both models once)
│   │   ├── api/                    # health, ecg, ecg-image, history, statistics, model
│   │   ├── ml/                     # model loaders, predictors, preprocessing,
│   │   │                           # image_interpretation.py, image_gradcam.py, explainability.py
│   │   ├── database/               # database.py, models.py, schemas.py
│   │   ├── services/               # ecg_service, image_service, report_service, summary_service
│   │   └── core/                   # config.py (env), logging.py
│   ├── config/model_config.json    # signal model config (real)
│   ├── models/ptbxl_cnn_best.pt    # signal checkpoint
│   ├── models/image/               # image checkpoint + model_config.json
│   ├── uploads/  reports/  tests/  # uploaded files, generated PDFs, pytest suite
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/             # layout, dashboard, ecg, results, assistant,
│   │   │                           # image-analysis (uploader, preview, gradcam, pattern assessment)
│   │   ├── pages/                  # Landing, Dashboard, AnalyzeECG, Results, History, Analytics,
│   │   │                           # ModelInfo, Settings, Help, AnalysisDetails
│   │   ├── services/  hooks/  utils/  assets/  context/
│   │   └── App.jsx  main.jsx  index.css
│   ├── index.html  vite.config.js  tailwind.config.js  package.json
├── data/                           # PTB-XL metadata + sample ECGs
├── model_reference/                # original notebook, architecture, preprocessing (untouched)
├── ecg-image-model/                # original image-model package (untouched source of truth)
├── docs/                           # architecture.md, api.md, model.md
├── tools/
├── docker-compose.yml
├── Dockerfile.backend / Dockerfile.frontend
├── MODEL_INTEGRATION.md  README.md  LICENSE
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+** (tested with 3.14) and `pip`
- **Node.js 18+** and npm
- PostgreSQL if you want production storage (SQLite is default)

### 1️⃣ Backend

```bash
cd backend
py -3 -m pip install -r requirements.txt
copy .env.example .env      # adjust paths if needed
py -3 -m uvicorn app.main:app --reload --port 8000
```

Verify: open **http://localhost:8000/docs** (Swagger) and check **GET /api/health** returns
`{"status":"ok","model_loaded":true,"image_model_loaded":true,...}`.

> On Windows, use `py -3` and `npm.cmd` (see Troubleshooting).

### 2️⃣ Frontend

```bash
cd frontend
npm install
npm run dev                 # http://localhost:5173
```

The Vite dev server proxies `/api` → `http://localhost:8000` automatically.

---

## ⚙ Configuration

All settings come from environment variables (see `backend/.env.example`):

| Variable | Default | Purpose |
|---|---|---|
| `SIGNAL_MODEL_PATH` | `models/ptbxl_cnn_best.pt` | Signal checkpoint path |
| `IMAGE_MODEL_PATH` | `models/image/best_model.pt` | Image checkpoint path |
| `IMAGE_MODEL_CONFIG` | `models/image/model_config.json` | Image config (classes, normalization) |
| `ENABLE_IMAGE_MODEL` | `true` | Set `false` to disable the image pipeline entirely |
| `DATABASE_URL` | `sqlite:///./cardiosense.db` | Storage connection string |
| `CORS_ORIGINS` | `http://localhost:5173` | Allowed frontend origins |
| `MAX_UPLOAD_SIZE_MB` | `20` | Max image upload size |
| `MODEL_VERSION` | `1.0` | Version reported by the API |
| `ENVIRONMENT` | `development` | `development` → debug logging |

---

## 🐳 Docker

```bash
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend: http://localhost:8000

---

## 🖥 Using the App

1. Open **http://localhost:5173** and click **Analyze ECG**.
2. Choose **ECG Signal** or **ECG Image** with the mode selector.
3. **Signal** — upload a 12-lead ECG. A sample pair lives at `data/sample_ecg/00001_lr.hea` +
   `.dat` (normal) — upload both files together.
   **Image** — upload a PNG/JPG/JPEG of an ECG (≤ 20 MB); preview is shown before analysis.
4. **Results** show prediction, confidence, probabilities, and:
   - *Signal:* ECG waveform, statistics, Integrated Gradients explainability.
   - *Image:* uploaded image, real Grad-CAM overlay, ECG Pattern Assessment (subclass labels,
     group bars, report, next steps, confidence & limitations).
5. Export a **PDF report** or ask the **Assistant** questions about the analysis.
6. Track everything on **Dashboard**, **History** (with Signal/Image filter), and **Analytics**
   (separate signal and image prediction distributions).

---

## 🔌 API Overview

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Service + model health |
| `POST` | `/api/ecg/analyze` | Analyze an ECG signal |
| `GET` | `/api/ecg/{id}` | Fetch a signal analysis |
| `GET` | `/api/ecg/report/{id}` | Signal PDF report |
| `POST` | `/api/ecg/{id}/summary` | Plain-language signal summary |
| `POST` | `/api/ecg/{id}/assistant` | Ask the assistant about a signal |
| `POST` | `/api/ecg-image/analyze` | Analyze an ECG image |
| `GET` | `/api/ecg-image/{id}` | Fetch an image analysis (enriched interpretation) |
| `GET` | `/api/ecg-image/{id}/image` | Stored uploaded image (PNG) |
| `GET` | `/api/ecg-image/{id}/gradcam` | Stored Grad-CAM overlay (PNG) |
| `GET` | `/api/ecg-image/report/{id}` | Image PDF report (incl. pattern assessment) |
| `POST` | `/api/ecg-image/{id}/summary` `…/assistant` | Image summary / assistant chat |
| `GET` | `/api/history`, `/api/statistics`, `/api/model/*` | History, analytics, model info |

Full reference: [`docs/api.md`](docs/api.md) + interactive docs at `/docs`.

---

## 🧪 Testing

```bash
cd backend
py -3 -m pytest tests -v
```

The suite (32 tests) covers health, both model loaders, preprocessing shapes, prediction, image
upload endpoints, Grad-CAM, interpretation (label mapping + group aggregation), distribution
verification, report fields, history, validation, and database behavior.

---

## 🛠 Troubleshooting

- **Port already in use** — change `--port` for uvicorn and the Vite proxy / `VITE_API_BASE_URL`.
- **Signal model not loading** — confirm `SIGNAL_MODEL_PATH` → `ptbxl_cnn_best.pt` and torch is
  installed. Check `/api/model/status`.
- **Image model not loading** — confirm `IMAGE_MODEL_PATH`/`IMAGE_MODEL_CONFIG` and
  `ENABLE_IMAGE_MODEL=true`. The signal pipeline still works (`image_model.loaded: false`).
- **CORS errors** — make sure `CORS_ORIGINS` includes your frontend origin (e.g. `http://localhost:5173`).
- **Windows blocks `npm`** — use `npm.cmd` instead of `npm`.
- **PDF download fails** — check `backend/reports/` is writable and ReportLab is installed.

---

## 🔒 Security

- Model checkpoints are read from disk only; they are **never** exposed through API routes.
- Uploads are validated by extension, MIME type, size, and decodability.
- Production secrets come from environment variables — never commit real `.env` values.
- Errors are logged in detail server-side but shown generically to users.

---

## 🌍 Deployment

- **DB:** PostgreSQL (`DATABASE_URL=postgresql://…`). Schema is created via SQLAlchemy
  `create_all`; existing SQLite DBs are upgraded in place by `_migrate_sqlite()`.
- **Frontend:** `npm run build` → serve `dist/` behind a static server.
- **Backend:** run uvicorn behind a reverse proxy (Docker ready).
- `models/image/best_model.pt` + `model_config.json` must be deployed with the app.

---

## ⚠️ Medical Disclaimer

CardioSense AI provides AI-generated ECG **signal and image** analysis for research and
decision-support purposes only.

**It is not a medical diagnosis and does not replace evaluation by a qualified healthcare
professional.** Model confidence values are measures of pattern similarity — they are **not**
disease, risk, or outcome probabilities. Always consult a clinician for any medical decision. If you
have serious symptoms (chest pain, severe shortness of breath, fainting, etc.), **seek urgent
medical attention immediately.**

---

## 📄 License

See [LICENSE](LICENSE).#   C a r d i o S e n s e - A I  
 