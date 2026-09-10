# Model Integration

This document explains how the two real trained PyTorch models (signal + image) are integrated into
CardioSense AI. The two pipelines are fully independent — they share the database/UI but never
interact at the model level.

## 1. ECG Signal Model (ECGCNN)

### Source of Truth

The following assets were inspected **before** writing any inference code:

| File | Role |
|---|---|
| `model_reference/ECG_MODEL.ipynb` | Original training notebook (untouched) |
| `model_reference/model_architecture.txt` | Layer-by-layer architecture |
| `model_reference/preprocessing_original.py` | Original preprocessing pipeline |
| `model_reference/ptbxl_cnn_best.pt` | Trained checkpoint |
| `model_config.json` | Input/output config, classes, thresholds |

### Findings (verified)

1. **Architecture**: 1D CNN (ECGCNN), NOT a CNN+Transformer. No attention mechanism exists in the
   checkpoint. Therefore explainability uses **Integrated Gradients**, not attention maps.
2. **Input shape**: `(12, 1000)` — 12 leads × 1,000 time samples.
3. **Sampling rate**: 100 Hz → 10 seconds of signal.
4. **Output**: 5 logits (multi-label), sigmoid activated, per-class thresholds.
5. **Classes**: `NORM, MI, STTC, CD, HYP`.
6. **Checkpoint format**: PyTorch `state_dict`.
7. **Preprocessing**: Butterworth bandpass (0.5–40 Hz, order 4) + per-record z-score. The production
   code at `backend/app/ml/preprocessing.py` implements exactly this pipeline.

### Integration Rules (signal)

- The model loads **once** at application startup (see `backend/app/main.py` lifespan →
  `backend/app/ml/model.py::ModelLoader`).
- Uses CUDA when available, otherwise CPU.
- Model path comes from the `SIGNAL_MODEL_PATH` environment variable (defaults to
  `backend/models/ptbxl_cnn_best.pt`).
- Predictions come only from the real model — no faking, no random outputs, no hardcoded results.
- All displayed metrics (AUC, thresholds, architecture) are read from the actual config/notebook.

### Verification (signal)

- `backend/tests/test_ml.py` loads the model and runs a synthetic signal through preprocessing +
  prediction.
- Real WFDB records from the PTB-XL sample data were processed end-to-end through the upload API
  and produced correct, sane predictions (e.g. record 00001 → Normal, record 00008 → Myocardial
  Infarction).

## 2. ECG Image Model (EfficientNet-B0)

### Source of Truth

The existing trained package `ecg-image-model/` was inspected **before** writing any integration
code. Its files are the authoritative reference and were reused directly (only copied, never
retrained or rewritten):

| File | Role |
|---|---|
| `ecg-image-model/models/best_model.pt` | Trained checkpoint |
| `ecg-image-model/models/model_config.json` | Classes, class mapping, input size, normalization |
| `ecg-image-model/src/model.py` | `create_model` → torchvision `efficientnet_b0` |
| `ecg-image-model/src/transforms.py` | `eval_transforms` (Resize 244 → CenterCrop 224) |
| `ecg-image-model/src/predict.py` | Preprocess + prediction |
| `ecg-image-model/src/gradcam.py` | Real Grad-CAM implementation |
| `ecg-image-model/MODEL_CARD.md` | Training metrics, dataset size |

### Findings (verified)

1. **Architecture**: torchvision `efficientnet_b0(weights=None)` with `classifier[1]` replaced by
   `nn.Linear(in_features, 15)` — transfer-learned to 15 classes.
2. **Input**: RGB image resized to `(244, 244)` then center-cropped to `(224, 224)`.
3. **Normalization**: ImageNet statistics — mean `[0.485, 0.456, 0.406]`, std `[0.229, 0.224, 0.225]`.
4. **Classes (15)**: `A, E, F, J, L, N, Q, R, S, V, aa, e, f, j, p` (from `class_mapping`).
5. **Output**: 15-class softmax probabilities; prediction = argmax.
6. **Checkpoint**: PyTorch `state_dict` under `model_state_dict`, epoch 20,
   `best_metric` = `val_macro_f1` 0.7019, plus `class_mapping`, `input_size`, `normalization`.
7. **Grad-CAM**: hooks `model.features[-1]` (last conv block), produces an overlay heatmap —
   implemented in `backend/app/ml/image_gradcam.py` mirroring `src/gradcam.py`.

### Integration Rules (image)

- The model loads **once** at application startup (lifespan in `backend/app/main.py` →
  `backend/app/ml/image_model.py::ImageModelLoader`). A load failure never affects the signal
  pipeline (`image_model_loader._load_error` is recorded and surfaced via status).
- Uses CUDA when available, otherwise CPU.
- Paths come from `IMAGE_MODEL_PATH` / `IMAGE_MODEL_CONFIG` env vars (defaults to
  `backend/models/image/best_model.pt` + `model_config.json`). `ENABLE_IMAGE_MODEL` can disable it.
- Preprocessing uses the exact training-compatible transforms from `src/transforms.py`
  (Resize 244 → CenterCrop 224 → ToTensor → ImageNet Normalize) — see `image_predictor._build_transforms`.
- Predictions, probabilities, confidence, and Grad-CAM come only from the real model.
- A Grad-CAM failure degrades gracefully: prediction succeeds and `gradcam_available` is `false`.

### Verification (image)

- `backend/tests/test_ml.py` verifies loader, preprocessing shape `(1, 3, 224, 224)`,
  prediction (15 probabilities), and Grad-CAM support.
- `backend/tests/test_api.py` verifies the upload endpoint end-to-end: `/api/ecg-image/analyze`,
  retrieval, Grad-CAM file, model status/info.
- A synthetic ECG-like image produced a real prediction (class `Q`, confidence ~0.41 with the
  low-confidence warning) and a saved Grad-CAM overlay.

### Image Interpretation Layer (pattern assessment)

On top of the raw 15-class output, `backend/app/ml/image_interpretation.py` derives a deterministic
pattern assessment — no additional model, no retraining:

- **Human-readable labels**: each of the 15 raw classes maps to a display name
  (e.g. `Q` → "Unclassifiable Beat", `S` → "Supraventricular Premature Beat").
- **Higher-level groups** (aggregated probability = sum of member subclass probabilities):
  `Normal` = N+L+R+e+j, `Supraventricular` = A+J+S+aa, `Ventricular` = V+E, `Fusion` = F,
  `Other/Unclassifiable` = Q+p+f.
- **Distribution check**: `verify_distribution` confirms the 15 probabilities sum to 1 (tolerance
  `1e-2`) before aggregation; results include `distribution_verified`.
- **Report / next steps / disclaimer**: descriptive text generated from the model output and the
  chosen confidence thresholds (high ≥ 0.60, moderate ≥ 0.40). It never hard-codes probabilities,
  never converts model output into disease/risk/mortality, and always states the assessment is not a
  diagnosis and warrants professional review.
- These fields are served on POST `/api/ecg-image/analyze` and GET `/api/ecg-image/{id}`; for stored
  records they are recomputed deterministically from the saved `probabilities`, so records that
  predate the feature are re-enriched on read.
- The Results page renders them as an "ECG Pattern Assessment" section (group bars, all 15
  subclasses sorted by probability, report rows, confidence & limitations, next steps), and the PDF
  report includes the pattern group summary with human-readable labels.

## Shared API Surface

- `GET /api/model/status` → `{ signal_model: {...}, image_model: {...} }` (each with `loaded`,
  `model_name`, `model_version`, `device`).
- `GET /api/model/image-info` → image model config (architecture, classes, normalization, input size).
- Statistics and history are filtered by `analysis_type` (signal/image) — see `docs/api.md`.
- DB rows store `analysis_type`, `model_name`, `image_path`, `gradcam_path`, `gradcam_available`.
  Existing rows are preserved; the SQLite schema is upgraded in place by `_migrate_sqlite()`.

## Degradation Behavior

- If the signal checkpoint is missing/corrupt, `/api/model/status` reports
  `signal_model.loaded: false`. The app still starts.
- If the image checkpoint is missing/corrupt (or disabled), the app still starts; the image
  endpoints return a clear error while the signal pipeline continues to work.
- Explainability degrades gracefully in both pipelines: signal Integrated Gradients falls back to
  `{"error": "..."}`, and image Grad-CAM sets `gradcam_available: false` rather than fabricating
  attribution.
