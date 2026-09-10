# API Documentation

Base URL: `http://localhost:8000`
Interactive docs (Swagger UI): [http://localhost:8000/docs](http://localhost:8000/docs)

CardioSense AI exposes two independent analysis pipelines under `/api/ecg/**` (signal) and
`/api/ecg-image/**` (image).

## Endpoints

### GET `/api/health`

Health check and model status.

```json
{
  "status": "ok",
  "model_loaded": true,
  "image_model_loaded": true,
  "device": "cpu",
  "version": "1.0"
}
```

### POST `/api/ecg/analyze` (also `/api/ecg/upload`)

Upload and analyze an ECG recording. Accepts `multipart/form-data` with one or more `files`.

- WFDB pair: send both `.hea` and `.dat`.
- Single files: `.mat`, `.csv`, `.npy`, `.txt`.

Validation: extension, size (max 20 MB), empty file, number of leads (12), sampling rate (100 Hz),
signal length, missing/corrupt values.

Returns:

```json
{
  "success": true,
  "message": "ECG analyzed successfully",
  "analysis_id": 1,
  "prediction": {
    "prediction": "Myocardial Infarction",
    "prediction_code": "MI",
    "confidence": 0.7944,
    "probabilities": { "Normal": 0.677, "Myocardial Infarction": 0.794, "..." : "..." },
    "all_predictions": { "Normal": true, "Myocardial Infarction": true, "..." : "..." },
    "signal_quality": "fair",
    "sampling_rate": 100,
    "duration": 10.0,
    "num_leads": 12,
    "model_version": "1.0",
    "processing_time": 0.0079,
    "explainability": { "method": "integrated_gradients", "lead_importance": {...}, "time_importance": [...] },
    "ecg_statistics": { "I": {...}, "...": "...", "overall": {...} },
    "signal_data": [[...], "..."]
  }
}
```

### GET `/api/ecg/{id}`

Fetch a single analysis by id.

### DELETE `/api/ecg/{id}`

Delete an analysis.

### GET `/api/ecg/history`

Paginated, filterable, sortable list.

Query params: `page`, `page_size` (default 10), `search` (file name), `prediction` (code),
`analysis_type` (`signal`/`image`), `sort_by`, `sort_order` (`asc`/`desc`).

```json
{
  "items": [ { ... analysis ... } ],
  "total": 12,
  "page": 1,
  "page_size": 10,
  "total_pages": 2
}
```

### POST `/api/ecg-image/analyze`

Upload and analyze an ECG image. Accepts `multipart/form-data` with one `file` (PNG/JPG/JPEG,
max 20 MB).

Validation: extension, MIME type, empty file, size, and decodability.

Returns:

```json
{
  "success": true,
  "message": "ECG image analyzed successfully",
  "analysis_id": 3,
  "analysis_type": "image",
  "file_name": "ecg.png",
  "prediction": "Q",
  "confidence": 0.4101,
  "probabilities": { "A": 0.001, "Q": 0.4101, "..." : "..." },
  "model": { "name": "EfficientNet-B0", "version": "1.0" },
  "processing_time": 0.021,
  "gradcam_available": true,
  "warning": "Low model confidence. The ECG image may be difficult to classify reliably.",
  "distribution_verified": true,
  "primary_prediction": "Q",
  "primary_label": "Unclassifiable Beat",
  "primary_confidence": 0.4101,
  "dominant_group": "Other/Unclassifiable",
  "group_probabilities": { "Normal": 0.139, "Supraventricular": 0.096, "Ventricular": 0.022, "Fusion": 0.045, "Other/Unclassifiable": 0.698 },
  "subclass_results": [
    { "raw_class": "Q", "human_readable_label": "Unclassifiable Beat", "probability": 0.4101, "group": "Other/Unclassifiable", "group_probability": 0.698 }
  ],
  "report": {
    "dominant_pattern": "...",
    "strongest_group": "...",
    "confidence_assessment": "...",
    "not_a_diagnosis": "This is an AI-based model assessment, not a medical diagnosis.",
    "warrants_professional_review": true
  },
  "next_steps": [ "..." ],
  "confidence_note": "...",
  "medical_disclaimer": "..."
}
```

> `warning` is present only when confidence < 0.60.
>
> `distribution_verified` confirms the 15 subclass probabilities form a single normalized
> distribution before group aggregation. The 5 `group_probabilities` are sums of their member
> subclasses (Normal = N+L+R+e+j, Supraventricular = A+J+S+aa, Ventricular = V+E, Fusion = F,
> Other/Unclassifiable = Q+p+f). `subclass_results` lists all 15 subclasses sorted by probability
> with human-readable labels. `report`/`next_steps`/`confidence_note`/`medical_disclaimer` are
> descriptive text derived deterministically from the model output — never hard-coded
> probabilities, and never a diagnosis or risk assessment.

### GET `/api/ecg-image/{id}`

Fetch a single image analysis by id (404 if not an image analysis).

### GET `/api/ecg-image/{id}/image`

Returns the stored uploaded image as a PNG file.

### GET `/api/ecg-image/{id}/gradcam`

Returns the stored Grad-CAM overlay as a PNG file (404 if `gradcam_available` is false).

### GET `/api/ecg-image/report/{id}`

Returns a generated PDF report for an image analysis (`application/pdf`).

### POST `/api/ecg-image/{id}/summary`

Generates a plain-language summary from image analysis data.

### POST `/api/ecg-image/{id}/assistant`

Body (form): `question=...`. Answers using only in-app image analysis data.

### GET `/api/statistics`

Aggregate statistics computed live from the database.

```json
{
  "total_analyses": 12,
  "signal_count": 7,
  "image_count": 5,
  "normal_count": 5,
  "abnormal_count": 7,
  "average_confidence": 0.78,
  "prediction_distribution": { "Normal": 5, "Myocardial Infarction": 4, "..." : "..." },
  "image_prediction_distribution": { "Q": 2, "N": 3, "..." : "..." },
  "confidence_distribution": { "70-80%": 3, "..." : "..." },
  "trend_data": [ { "date": "2026-08-07", "count": 3 } ],
  "most_common_prediction": "Normal",
  "average_processing_time": 0.01
}
```

### GET `/api/model/info`

Real signal model configuration from `model_config.json`.

### GET `/api/model/status`

Runtime model status for both models:

```json
{
  "signal_model": {
    "loaded": true,
    "model_name": "ECGCNN",
    "model_version": "1.0",
    "num_classes": 5,
    "input_shape": [12, 1000],
    "device": "cpu"
  },
  "image_model": {
    "loaded": true,
    "model_name": "EfficientNet-B0",
    "model_version": "1.0",
    "num_classes": 15,
    "input_size": [224, 224],
    "device": "cpu"
  }
}
```

### GET `/api/model/image-info`

Real image model configuration: architecture, classes (15), class mapping, `input_size`,
normalization, Grad-CAM support (`"gradcam_supported": true`), framework, loaded state.

### GET `/api/ecg/report/{id}`

Returns a generated PDF report (`application/pdf`).

### POST `/api/ecg/{id}/summary`

Generates a plain-language AI summary from analysis data.

### POST `/api/ecg/{id}/assistant`

Body (form): `question=...`. Answers using only in-app analysis data.

## Error Handling

Errors return JSON with a friendly `detail` message. Detailed server logs contain full stack traces,
but they are never exposed to clients. Common codes: 400 (validation), 404 (not found),
413 (too large), 500 (internal).
