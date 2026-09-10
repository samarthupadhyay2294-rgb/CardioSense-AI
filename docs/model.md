# Model Documentation

CardioSense AI runs two independent, real models: the ECG signal model (ECGCNN) and the ECG image
model (EfficientNet-B0).

---

## 1. ECG Signal Model (ECGCNN)

### Summary

- `Name`: ECGCNN
- `Version`: 1.0
- `Architecture`: 1D Convolutional Neural Network (no Transformer)
- **Framework**: PyTorch
- **Parameters**: 338,725
- **Input**: `(12, 1000)` — 12 leads × 1,000 samples
- **Sampling rate**: 100 Hz (10-second recording)
- **Output**: 5 logits (BCE-with-logits → sigmoid probabilities)
- **Dataset**: PTB-XL (train 17,111 / val 2,156 / test 2,163)

### Architecture (verified against `model_architecture.txt`)

```
Conv1d(12→32, k=7, p=3) → BatchNorm → ReLU → MaxPool(2)   # (32, 500)
Conv1d(32→64, k=7, p=3)  → BatchNorm → ReLU → MaxPool(2)   # (64, 250)
Conv1d(64→128, k=7, p=3) → BatchNorm → ReLU → MaxPool(2)   # (128, 125)
Conv1d(128→256, k=7, p=3)→ BatchNorm → ReLU → MaxPool(2)   # (256, 62)
AdaptiveAvgPool1d(1)                                       # (256, 1)
Linear(256→128) → ReLU → Dropout(0.4) → Linear(128→5)      # 5 logits
```

### Classes

| Code | Name | Validation Threshold |
|---|---|---|
| NORM | Normal | 0.3233 |
| MI | Myocardial Infarction | 0.5394 |
| STTC | ST/T Changes | 0.5181 |
| CD | Conduction Disturbance | 0.4473 |
| HYP | Hypertrophy | 0.5002 |

Multi-label output: a class is considered detected when its sigmoid probability is ≥ its threshold.

### Preprocessing (from `preprocessing.py`)

1. Ensure shape is `(leads, samples)`.
2. Butterworth bandpass 0.5–40 Hz, order 4, at 100 Hz (applied along time axis).
3. Per-record z-score per lead: `(x - mean) / (std + 1e-8)`.
4. Return `(samples, leads)` float32 (transposed for the CNN).

### Training Configuration

- Batch size: 64, Epochs: 30, LR: 1e-3 (Adam, ReduceLROnPlateau)
- Loss: `BCEWithLogitsLoss` with positive-class weights `[1.25, 2.90, 3.08, 3.37, 7.07]`
- Best model selected by validation loss

### Test Metrics (from the training notebook)

| Class | AUC |
|---|---|
| NORM | 0.9413 |
| MI | 0.9252 |
| STTC | 0.9350 |
| CD | 0.9230 |
| HYP | 0.8395 |
| **Mean Test AUC** | **0.9128** |

### Explainability

Integrated Gradients (50 steps, zero baseline) is used to attribute the prediction to input regions.
Attention maps are not applicable (no Transformer). For NORM predictions, explainability is skipped.

### Checkpoint

`backend/models/ptbxl_cnn_best.pt` — PyTorch `state_dict`. Loaded once at startup.

**Source of truth**: The original files (notebook, architecture, preprocessing) are preserved
unmodified in `model_reference/`.

---

## 2. ECG Image Model (EfficientNet-B0)

### Summary

- `Name`: EfficientNet-B0
- `Version`: 1.0
- `Architecture`: torchvision `efficientnet_b0` (transfer-learned) with the final classifier replaced
  by `nn.Linear(in_features, 15)`
- `Framework`: PyTorch
- `Input`: RGB image resized to `(244, 244)` then center-cropped to `(224, 224)`
- `Normalization`: ImageNet — mean `[0.485, 0.456, 0.406]`, std `[0.229, 0.224, 0.225]`
- `Output`: 15-class softmax probabilities; prediction = argmax
- `Dataset`: 54,613 images (from `ecg-image-model/MODEL_CARD.md`)

### Classes

`A, E, F, J, L, N, Q, R, S, V, aa, e, f, j, p` (15 classes from `class_mapping` in
`model_config.json`).

### Preprocessing (from `ecg-image-model/src/transforms.py` — reused as-is)

1. Resize to `(244, 244)`.
2. CenterCrop to `(224, 224)`.
3. Convert to float tensor.
4. Normalize with ImageNet mean/std.

Implemented in `backend/app/ml/image_predictor.py::_build_transforms`, which reads the actual
`input_size` / `normalization` values from the image `model_config.json` (never hardcoded).

### Training Configuration (from the checkpoint)

- Epochs: 20, best epoch metric: `val_macro_f1 = 0.7019`
- Checkpoint keys: `model_state_dict`, `epoch`, `best_metric`, `class_mapping`, `input_size`,
  `normalization`, `training_configuration`

### Model-Card Metrics (from `ecg-image-model/MODEL_CARD.md`)

| Metric | Value |
|---|---|
| Accuracy | 0.9384 |
| Balanced accuracy | 0.8968 |
| Macro precision | 0.6475 |
| Macro recall | 0.8370 |
| Macro F1 | ~0.690 |

### Explainability (Grad-CAM)

`backend/app/ml/image_gradcam.py` mirrors `ecg-image-model/src/gradcam.py`: it registers hooks on
`model.features[-1]` (last convolutional block), computes the class-discriminative activation map for
the predicted class, and overlays a heatmap on the original image. If Grad-CAM fails, the prediction
still succeeds and `gradcam_available` is `false`.

### Checkpoint

`backend/models/image/best_model.pt` + `backend/models/image/model_config.json` — copied from the
existing trained package, loaded once at startup via `backend/app/ml/image_model.py`.

**Source of truth**: `ecg-image-model/` is preserved unmodified and is never retrained or rewritten.
