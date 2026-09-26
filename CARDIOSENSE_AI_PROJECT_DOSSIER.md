# CardioSense AI: Project Dossier

## 1. Executive Summary

CardioSense AI is a full-stack web application for **research and educational ECG analysis**. It accepts either a digital 12-lead ECG signal or an ECG image, runs a trained PyTorch model, and presents model outputs with visual explanations, reports, history, and analytics.

The system has two deliberately independent AI pipelines:

1. **Signal pipeline**: classifies 12-lead ECG recordings into five PTB-XL diagnostic superclasses.
2. **Image pipeline**: classifies an ECG image into one of fifteen beat subclasses and aggregates those probabilities into five broader pattern groups.

The application explicitly states that it is **not a medical diagnostic device**. Its appropriate use is experimentation, learning, research, and decision-support prototyping under qualified clinical review.

---

## 2. Project Goals

CardioSense AI aims to:

- Accept common ECG recording formats and ECG images.
- Run inference using real, locally stored, trained model checkpoints.
- Display prediction probabilities rather than only a single label.
- Explain model behavior with Integrated Gradients for signal data and Grad-CAM for images.
- Preserve analyses in a database and make them searchable.
- Create downloadable PDF reports.
- Provide aggregate analytics, simulation, batch processing, and model-performance views.
- Keep safety boundaries visible through disclaimers and non-diagnostic language.

---

## 3. Technology Stack

| Area | Technology |
|---|---|
| Client application | React 18, Vite 6, React Router |
| Styling and interaction | Tailwind CSS, Framer Motion, Lucide icons |
| Charts | Recharts, Plotly |
| API | FastAPI, Uvicorn |
| Database access | SQLAlchemy 2 |
| ML runtime | PyTorch, torchvision, NumPy, SciPy |
| ECG file support | WFDB |
| Image handling | Pillow, OpenCV |
| Reports | ReportLab |
| Local persistence | SQLite by default |
| Container deployment | Docker Compose, PostgreSQL 16 |

### 3.1 Complete frontend stack

| Package or tool | Version declared in project | Role in the project |
|---|---:|---|
| React | 18.3.1 | Component-based browser user interface |
| React DOM | 18.3.1 | Renders React into the browser DOM |
| React Router DOM | 6.28.0 | Client-side navigation between application pages |
| Vite | 6.0.7 | Development server and frontend production build tool |
| `@vitejs/plugin-react` | 4.3.4 | React support for Vite |
| Tailwind CSS | 3.4.17 | Utility-first visual styling and responsive layout |
| PostCSS | 8.4.49 | CSS transformation pipeline |
| Autoprefixer | 10.4.20 | Browser-vendor CSS prefix handling |
| Framer Motion | 11.15.0 | UI animation and transitions |
| Lucide React | 0.469.0 | SVG icon components |
| Recharts | 2.15.0 | Dashboard, analytics, probability, and trend charts |
| Plotly.js Dist Min | 2.35.2 | Interactive plotting support |
| React Plotly.js | 2.6.0 | React integration for Plotly charts |
| Node.js | 18+ required; Node 20 in Docker | Package runtime, frontend build, and static hosting |
| `serve` | Installed in final Docker image | Hosts the built React single-page application |

### 3.2 Complete backend stack

| Package or tool | Version declared in project | Role in the project |
|---|---:|---|
| Python | 3.11+ required | Main backend and ML language |
| FastAPI | 0.115.6 | HTTP API framework, validation, OpenAPI/Swagger generation |
| Uvicorn | 0.34.0 | ASGI server that runs FastAPI |
| Pydantic | 2.10.4 | Request, response, and settings data validation |
| Pydantic Settings | 2.7.0 | Environment-based application configuration |
| SQLAlchemy | 2.0.36 | ORM and database access |
| PyTorch | 2.1+ | Signal and image model inference |
| torchvision | 0.16+ | EfficientNet-B0 architecture and image transforms |
| NumPy | 1.24+ | Array manipulation and numerical processing |
| SciPy | 1.10+ | Signal filtering, resampling, feature calculations |
| WFDB | 4.1+ | Reading WFDB ECG records and metadata |
| Pillow | 10+ | Image decoding, conversion, and validation |
| OpenCV headless | 4.8+ | Image-processing support for the Grad-CAM workflow |
| ReportLab | 4.2.5 | PDF report generation |
| python-multipart | 0.0.20 | Multipart file upload parsing in FastAPI |
| python-dotenv | 1.0.1 | Environment-variable loading support |
| psycopg2-binary | 2.9.10+ | PostgreSQL database driver |
| websockets | 12+ | Declared transport dependency for future streaming support |
| pytest | 8.3.4 | Backend test execution |
| HTTPX | 0.28.1 | HTTP test client and request support |

### 3.3 Data, model, and runtime assets

| Asset | Purpose |
|---|---|
| PTB-XL metadata CSV | Metadata and labels for the signal dataset |
| PTB-XL 100 Hz records | WFDB waveforms used for examples and intended evaluation |
| `ptbxl_cnn_best.pt` | Trained ECGCNN signal model checkpoint |
| `model_config.json` | Signal model classes, thresholds, preprocessing, and training configuration |
| `best_model.pt` | Trained EfficientNet-B0 image-model checkpoint |
| Image model configuration | Image classes, mapping, resolution, and normalization values |
| SQLite | Default local application database |
| PostgreSQL 16 | Docker deployment database option |
| Local filesystem directories | Uploads, Grad-CAM images, logs, and generated reports |

### 3.4 Infrastructure and development tooling

| Tool | Role |
|---|---|
| Docker | Containerizes the frontend and backend |
| Docker Compose | Starts frontend, backend, PostgreSQL, volumes, and ports together |
| Python slim Docker image | Backend runtime image |
| Node Alpine Docker image | Frontend build and static-serving image |
| Git | Source-control repository with active local changes |
| Swagger UI | Automatically generated FastAPI API documentation at `/docs` |

### 3.5 System interfaces

| Interface | Protocol / format | Use |
|---|---|---|
| Frontend to backend | HTTP, JSON, multipart form data | Standard application operations and file uploads |
| Signal upload | WFDB, MAT, CSV, NPY, TXT | 12-lead ECG ingestion |
| Image upload | PNG, JPG, JPEG | ECG image ingestion |
| Backend to models | In-process PyTorch tensors | Model inference |
| Backend to database | SQLAlchemy with SQLite or PostgreSQL | Persisted analysis history |
| Backend to reports | ReportLab PDF generation | Downloadable analysis reports |
| Batch export | CSV and JSON | External review of batch results |

---

## 4. Repository Structure

```text
ECG/
├── backend/
│   ├── app/
│   │   ├── api/                 FastAPI routes
│   │   ├── core/                configuration and logging
│   │   ├── database/            SQLAlchemy models and schemas
│   │   ├── ml/                  model loading, preprocessing, prediction, explainability
│   │   ├── services/            analysis, reporting, simulation, batch, evaluation
│   │   └── main.py              FastAPI application entry point
│   ├── config/model_config.json Signal model configuration
│   ├── models/                  trained signal and image model checkpoints
│   ├── tests/                   backend test suite
│   └── requirements.txt
├── frontend/
│   ├── src/components/          reusable UI components
│   ├── src/pages/               application pages
│   ├── src/services/api.js      API client for core workflows
│   └── public/                  logo and static assets
├── data/                        PTB-XL metadata and sample recording
├── records100/                  PTB-XL 100 Hz waveform records
├── ecg-image-model/             original image-model package and model card
├── model_reference/             signal-model source references
├── docs/                        architecture, API, and model documentation
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
├── README.md
└── MODEL_INTEGRATION.md
```

---

## 5. High-Level Architecture

```text
Browser
  |
  | React / Vite frontend
  v
FastAPI backend
  |
  +-- Signal analysis API ------ ECGCNN signal model
  |
  +-- Image analysis API ------- EfficientNet-B0 image model
  |
  +-- History, statistics, reports, simulation, batch processing
  v
SQLite development database or PostgreSQL deployment database
```

At application startup, FastAPI initializes the database and attempts to load both models once. The image model is isolated: a failure to load it does not intentionally prevent the signal-analysis workflow from starting.

### Main runtime sequence

1. The user selects a signal or image analysis mode in the React interface.
2. The frontend sends a multipart upload request to FastAPI.
3. The backend validates the input, runs the appropriate preprocessing and model inference flow, and creates analysis metadata.
4. The result is stored in the database.
5. The frontend renders the analysis result, visual explanation, interpretation, and download links.
6. Dashboard, history, and analytics views read the stored analysis records.

---

## 6. ECG Signal Analysis Pipeline

### 6.1 Supported input

The signal API accepts:

- WFDB pairs: `.hea` with `.dat`
- MATLAB: `.mat`
- CSV: `.csv`
- NumPy: `.npy`
- Text: `.txt`

The intended input is a **12-lead ECG sampled at 100 Hz for 10 seconds**, which corresponds to 1,000 time samples per lead.

### 6.2 Validation

The backend checks:

- File extension and maximum file size.
- Empty content.
- A two-dimensional signal shape.
- Twelve leads and 1,000 samples, in either lead-first or sample-first orientation.
- Missing or infinite values.
- All-zero signals.
- Sampling rate of exactly 100 Hz for formats that contain sampling-rate metadata.

### 6.3 Preprocessing

The processing steps mirror the documented signal-model configuration:

1. Arrange the signal as 12 leads by 1,000 samples.
2. Apply a fourth-order Butterworth band-pass filter from 0.5 Hz to 40 Hz.
3. Apply per-record z-score normalization.
4. Convert to a PyTorch tensor with shape `(1, 12, 1000)`.

### 6.4 Signal model

The signal model is named **ECGCNN**.

| Property | Value |
|---|---|
| Model type | 1-D convolutional neural network |
| Input | 12 leads × 1,000 samples |
| Output | 5 logits |
| Total parameters | 338,725 |
| Loss during training | BCEWithLogitsLoss |
| Optimizer | Adam |
| Training epochs in config | 30 |
| Inference activation | Sigmoid |
| Classification mode | Multi-label, threshold based |

The architecture uses four convolutional blocks with batch normalization, ReLU activation, max pooling, adaptive average pooling, two dense layers, and dropout.

### 6.5 Signal classes and thresholds

| Code | User-facing label | Configured threshold |
|---|---|---:|
| NORM | Normal | 0.3233 |
| MI | Myocardial Infarction | 0.5394 |
| STTC | ST/T Changes | 0.5181 |
| CD | Conduction Disturbance | 0.4473 |
| HYP | Hypertrophy | 0.5002 |

The sigmoid output enables more than one positive class. The frontend should therefore be understood as showing model evidence for each superclass, not a mutually exclusive diagnosis.

### 6.6 Signal outputs

For a successful analysis, the system returns and stores:

- Primary displayed prediction and confidence.
- Probability for all five classes.
- Boolean threshold results for all classes.
- Sampling rate, duration, lead count, processing time, and signal-quality label.
- Downsampled waveform data for browser visualization.
- Per-lead amplitude statistics.
- Estimated temporal, frequency, and morphological features.
- Integrated Gradients output for non-normal predictions, when successful.
- A structured interpretation layer and PDF report.

### 6.7 Feature-extraction caveat

The feature extractor estimates R peaks, RR intervals, heart rate, QRS duration, ST deviation, PR interval, QT interval, frequency bands, and morphology statistics. The code itself labels these as **estimated signal features** rather than clinically validated measurements. This distinction must be maintained in any demo, report, or presentation.

### 6.8 Complete signal-analysis workflow

```text
1. User opens Analyze ECG
2. User selects the signal-analysis mode
3. User uploads one supported file or one WFDB .hea + .dat pair
4. React creates FormData and sends POST /api/ecg/analyze
5. FastAPI validates file extension, size, and presence of files
6. ECG service reads the signal using WFDB, SciPy, NumPy, or text parsing
7. Backend verifies the 12-lead, 100 Hz, 1,000-sample requirements
8. Backend orients the matrix as 12 leads × 1,000 samples
9. Preprocessing applies the 0.5–40 Hz band-pass filter
10. Preprocessing applies per-record z-score normalization
11. ECGCNN produces five logits and sigmoid probabilities
12. Per-class thresholds determine the multi-label positive classes
13. Service calculates signal-quality label and per-lead statistics
14. Feature extractor derives estimated waveform features
15. Clinical interpretation service creates a structured, non-diagnostic summary
16. Integrated Gradients runs for a non-normal primary prediction when possible
17. Downsampled waveform data and results are persisted in ecg_analyses
18. API returns the analysis ID and complete response to React
19. Results page renders waveform, probabilities, explanation, interpretation, and report link
20. Dashboard, History, and Analytics read the stored record later
```

---

## 7. ECG Image Analysis Pipeline

### 7.1 Supported input

The image API accepts one PNG, JPG, or JPEG ECG image up to 20 MB. It validates extension, MIME type, non-empty content, size, and whether Pillow can decode the image.

### 7.2 Image preprocessing

The image pipeline:

1. Converts the image to RGB.
2. Resizes to 244 × 244.
3. Center-crops to 224 × 224.
4. Converts pixels to a tensor.
5. Applies ImageNet mean and standard-deviation normalization.

### 7.3 Image model

| Property | Value |
|---|---|
| Model | EfficientNet-B0 |
| Input | 224 × 224 RGB image |
| Output | 15-class softmax distribution |
| Prediction rule | Highest-probability class |
| Explainability | Grad-CAM over the final convolutional feature block |
| Reported training source | User-provided Kaggle ECG-image dataset |
| Reported dataset size | 54,613 images |

The model card reports a validation macro F1 of 0.7019. Its reported test metrics are 93.84% accuracy, 89.68% balanced accuracy, 64.75% macro precision, 83.70% macro recall, 69.00% macro F1, and 94.92% weighted F1. These are dataset-specific model-card values, not clinical-validation results.

### 7.4 Beat subclasses and grouped output

| Group | Subclasses |
|---|---|
| Normal | N, L, R, e, j |
| Supraventricular | A, J, S, aa |
| Ventricular | V, E |
| Fusion | F |
| Other / Unclassifiable | Q, p, f |

The raw classifier returns 15 probabilities. The interpretation layer checks that the distribution approximately sums to one, aggregates subclass probabilities into the five groups above, maps raw codes to human-readable labels, and produces descriptive next steps and safety notices. It does not train or invoke an additional diagnosis model.

### 7.5 Image outputs

- Primary subclass label and confidence.
- All 15 subclass probabilities.
- Five grouped pattern probabilities.
- Dominant group and human-readable pattern summary.
- Grad-CAM image, when generation succeeds.
- Confidence warning when confidence is below 0.60.
- Stored uploaded image and generated image report.

Grad-CAM highlights image regions that influence the neural-network output. It does not provide a clinical finding or prove that the highlighted area is medically causal.

### 7.6 Complete image-analysis workflow

```text
1. User opens Analyze ECG
2. User selects the image-analysis mode
3. User selects a PNG, JPG, or JPEG ECG image
4. The interface previews the selected image
5. React sends POST /api/ecg-image/analyze as multipart form data
6. FastAPI validates name, MIME type, byte size, and image decodability
7. Service stores a sanitized copy of the input image
8. Pillow converts the image to RGB
9. torchvision resizes to 244 × 244, center-crops to 224 × 224, and normalizes pixels
10. EfficientNet-B0 produces 15 logits and a softmax probability distribution
11. The largest probability becomes the primary beat subclass
12. Interpretation layer checks distribution normalization and maps codes to readable labels
13. Subclass probabilities aggregate into Normal, Supraventricular, Ventricular, Fusion, and Other groups
14. Grad-CAM attempts to create and save a heatmap overlay
15. The service creates confidence notes, descriptive next steps, and a safety disclaimer
16. The backend saves metadata, probabilities, image path, and Grad-CAM path in ecg_analyses
17. API returns the analysis ID and enriched pattern-assessment response
18. Results page displays the uploaded image, Grad-CAM, group bars, subclasses, and report link
```

---

## 8. Frontend Experience

The frontend routes include:

| Route | Purpose |
|---|---|
| `/` | Landing page |
| `/dashboard` | Recent activity and aggregate statistics |
| `/analyze` | Signal or image upload and analysis |
| `/results/:id` | Detailed result display |
| `/history` | Saved analysis list |
| `/history/:id` | Analysis detail/history view |
| `/analytics` | Prediction, confidence, trend, and timing charts |
| `/model` | Model configuration and status |
| `/settings` | Application settings |
| `/help` | Usage and help content |
| `/simulation` | Synthetic ECG generation and optional analysis |
| `/performance` | Intended evaluation metrics view |
| `/batch` | Multiple-file batch processing |

The visual interface includes responsive layout behavior, dark mode, chart components, waveform components, and image-analysis widgets such as preview, heatmap, and pattern-assessment views.

---

## 9. Backend API Surface

### Core operations

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Service and model status |
| POST | `/api/ecg/analyze` | Analyze an ECG signal |
| GET | `/api/ecg/{id}` | Retrieve a signal analysis |
| DELETE | `/api/ecg/{id}` | Delete an analysis record |
| POST | `/api/ecg-image/analyze` | Analyze an ECG image |
| GET | `/api/ecg-image/{id}` | Retrieve an image analysis |
| GET | `/api/statistics` | Live aggregate statistics |
| GET | `/api/ecg/history` | Paginated, filterable history |
| GET | `/api/model/info` | Signal-model configuration |
| GET | `/api/model/status` | Runtime signal and image model status |

### Supporting operations

| Area | Available capabilities |
|---|---|
| Reports | Signal and image PDF report endpoints |
| Summary and assistant | Record-grounded summary and question answering |
| Simulation | Generate or generate-and-analyze synthetic ECGs |
| Batch | Analyze up to 50 files, retrieve results, filter, export CSV/JSON |
| Performance | Status, metrics, confusion matrix, class metrics, and evaluation trigger |

---

## 10. Persistence and Reporting

The main `ecg_analyses` database entity stores analysis type, input metadata, prediction, confidence, probability distributions, signal metadata, explainability data, feature data, interpretation data, image paths, Grad-CAM paths, model details, timing, and timestamp.

Uploaded files, Grad-CAM images, and generated reports are saved in the server filesystem. SQLite is the development default. Docker Compose configures PostgreSQL for the database service.

Reports are generated through ReportLab and are available for both signal and image analyses. The product documentation states that report content includes disclaimer language.

---

## 11. Simulation, Batch Processing, and Analytics

### Simulation

The simulation service generates mathematically synthesized 12-lead ECG signals. Users can configure parameters such as selected abnormality, heart rate, noise level, baseline wander, and duration. It can either return a signal or send the generated signal into the existing model workflow. It is explicitly educational and is not a substitute for real patient data.

### Batch processing

The batch endpoint accepts up to 50 ECG files. It uses the existing single-file analysis service and returns a result for every item, including failure details. Users can filter results and export CSV or JSON. Results are stored in the service process memory rather than the database.

### Dashboard and analytics

Statistics are calculated from stored analysis records. Current views present:

- Total, signal, and image analysis counts.
- Normal and abnormal counts.
- Prediction distributions.
- Image prediction distributions.
- Confidence buckets.
- Daily analysis trends.
- Average processing time.
- Recent analyses.

These views describe the user’s local analysis history. They do not establish real-world clinical incidence or model generalizability.

### 11.1 History, analytics, and PDF-report workflow

```text
Completed signal or image analysis
  ↓
ECGAnalysis row stored in SQLite or PostgreSQL
  ↓
History endpoint retrieves records with paging, search, filtering, and sorting
  ↓
Dashboard and Analytics request aggregate statistics from stored rows
  ↓
Frontend renders counts, distributions, confidence buckets, trends, and recent activity
  ↓
User requests a report
  ↓
Report service reads the stored record and creates a PDF with ReportLab
  ↓
Browser downloads the generated PDF from the report endpoint
```

### 11.2 Batch-processing workflow

```text
1. User selects up to 50 files in the Batch Analysis page
2. Browser sends the file collection to POST /api/batch/analyze
3. API checks file count, extensions, and maximum size
4. Batch service generates a batch ID
5. Each file is saved and passed through the single-file signal-analysis service
6. Service records a success result or a classified failure result for each file
7. Batch result remains in the process-memory batch_results dictionary
8. Frontend renders total, successful, failed, and success-rate summaries
9. User filters results by status, prediction, or filename
10. User exports a CSV or JSON representation of the in-memory batch result
```

### 11.3 Simulation workflow

```text
1. User selects a simulated ECG pattern and parameters
2. Frontend sends parameters to /api/simulation/generate or /generate-and-analyze
3. ECG simulator creates a mathematical 12-lead waveform
4. Generate endpoint returns displayable waveform data and metadata
5. Generate-and-analyze endpoint sends the synthetic waveform through the signal predictor
6. Response includes simulated waveform, prediction, signal statistics, and disclaimer
7. Frontend plots the signal and displays the educational result
```

### 11.4 Deployment workflow

```text
Developer runs docker compose up --build
  ↓
Docker builds the Python backend image and Node frontend image
  ↓
Compose starts PostgreSQL, FastAPI backend, and static React frontend
  ↓
Backend mounts model/config/upload/report directories and connects to PostgreSQL
  ↓
Backend initializes database tables and attempts to load models once
  ↓
Frontend serves the built single-page application on port 5173
  ↓
Browser communicates with backend endpoints on port 8000
```

---

## 12. Deployment

### Local development

- Backend: Python 3.11+, `uvicorn app.main:app --reload --port 8000` from `backend/`.
- Frontend: Node.js 18+, `npm run dev` from `frontend/`.
- Frontend development server: `http://localhost:5173`.
- Backend API and Swagger: `http://localhost:8000` and `http://localhost:8000/docs`.

### Docker Compose

The compose configuration contains three services:

- `backend` on port 8000.
- `frontend` on port 5173.
- `db` using PostgreSQL 16 on port 5432.

The backend mounts model, configuration, upload, and report directories. Production deployment should replace local defaults with managed secrets, persistent storage, transport security, monitoring, and a hardened database configuration.

---

## 13. Testing

The repository includes backend test modules for:

- API routes.
- Model loading and inference.
- Batch API and batch processing.
- Clinical interpretation.
- Feature extraction.
- End-to-end integration.
- Model evaluation.
- Performance API.
- Simulation.

The frontend package provides development, production-build, and preview commands, but no dedicated frontend test framework is defined in `frontend/package.json`.

This dossier records source-level findings. It does not claim that the full test suite or production deployment was run successfully during preparation.

---

## 14. Strengths

- Uses locally available trained PyTorch checkpoints instead of fabricated predictions.
- Separates signal and image inference rather than combining incompatible inputs without validation.
- Applies appropriate visual explanation techniques for each model type.
- Supports several ECG signal formats.
- Includes useful product workflow features: history, reports, analytics, simulation, batch export, and result-grounded assistant responses.
- Includes visible disclaimers and explicitly avoids presenting itself as a clinical diagnostic product.
- Contains deployment scaffolding and a growing backend test suite.

---

## 15. Limitations and Identified Implementation Risks

### Product and clinical limitations

- The project is not clinically validated and should not make autonomous diagnostic decisions.
- The image-model card says that train/validation/test group or record-level separation was not verified.
- The image model was trained on a single dataset. Generalization to other scanners, ECG paper layouts, or care settings has not been demonstrated.
- Image-model softmax confidence is not a calibrated clinical probability.
- The ECG feature-extraction module uses simplified, estimated measurement logic.

### Privacy, security, and operations

- No authentication, authorization, or user isolation is implemented.
- Uploaded input, generated reports, waveform data, and predictions may constitute sensitive health information.
- The project needs encryption, audit logging, retention/deletion policy, secure storage, and access controls before real patient deployment.
- Docker Compose contains a visible default database password and is not production secrets management.
- Batch results are memory-resident and are lost when the application restarts.
- Deleting a database analysis row does not visibly remove the related upload, Grad-CAM, or report files.

### Current implementation gaps

- Documentation references real-time WebSocket streaming, but the current visible backend implementation exposes HTTP simulation endpoints; a dedicated WebSocket streaming route is not present in the inspected source.
- Batch processing defines a worker limit but processes files sequentially.
- Batch handling of WFDB `.hea` and `.dat` pairs is unreliable because the files are treated as separate batch items rather than one recording.
- Signal validation rejects recordings whose length differs from 1,000 samples before later resampling logic can execute.
- The signal fallback confidence for cases with no threshold-positive class uses `1 - P(NORM)`, which should be reviewed because it does not directly express confidence in a normal prediction.

### Performance-evaluation module: do not present signal metrics yet

The current evaluation implementation requires correction before using its figures in a presentation, demo, or report:

1. It imports `scikit-learn`, but `scikit-learn` is not declared in `backend/requirements.txt`.
2. It calls `predictor.get_model()`, although the inspected predictor class does not expose that method.
3. It returns `f1_weighted` from an undefined variable named `f1_weight`.
4. It evaluates a multilabel model as a single-label multiclass classifier, which conflicts with signal inference behavior.
5. It expects probability entries by raw class code, but the predictor returns human-readable probability keys. This makes ROC-AUC computation unreliable.
6. It preprocesses data before passing it to a predictor that preprocesses it again, creating a double-preprocessing issue.

Therefore, no calculated signal-model accuracy, F1, ROC-AUC, or confusion-matrix figure should be presented as validated until the evaluation code is repaired and rerun on a documented split.

---

## 16. Recommended Development Priorities

### Priority 1: Correctness and validation

1. Repair and rerun the signal-model evaluation pipeline.
2. Align multilabel prediction logic, labels, probabilities, thresholds, and metrics.
3. Add a documented test protocol and versioned evaluation outputs.
4. Fix WFDB-pair handling for batch uploads.
5. Reconcile streaming documentation with the implemented product.

### Priority 2: Security and data governance

1. Add authentication, role-based authorization, and user-specific records.
2. Protect files and database content with encryption and access policies.
3. Add secure secret management and remove default production credentials.
4. Implement artifact cleanup, retention rules, and audit logs.

### Priority 3: Production readiness

1. Move batch execution to durable jobs with progress persistence.
2. Add structured model monitoring, error monitoring, and operational logging.
3. Add frontend tests and full end-to-end tests.
4. Use object storage or managed persistent storage for uploads and reports.
5. Add load testing, rate limits, and robust API authorization.

---

## 17. PPT-Ready Storyline

Use the following 12-slide structure for an academic review, project defence, or product demonstration:

1. **Title**: CardioSense AI — Explainable ECG Signal and Image Analysis.
2. **Problem**: ECG interpretation is complex and time-sensitive; the project investigates research-oriented AI assistance.
3. **Objectives**: Analyze signals and images, explain outputs, maintain history, and generate reports.
4. **Solution Overview**: Introduce the two independent analysis pipelines.
5. **System Architecture**: React, FastAPI, two PyTorch models, database, reports, analytics.
6. **Signal Pipeline**: Input, preprocessing, ECGCNN, threshold-based outputs, Integrated Gradients.
7. **Image Pipeline**: Upload, EfficientNet-B0, 15 subclasses, groups, Grad-CAM.
8. **User Features**: Results, waveform display, image assessment, history, PDF reports, batch, simulation.
9. **Explainability and Safety**: Explain what Integrated Gradients and Grad-CAM provide; emphasize non-diagnostic use.
10. **Image-Model Results**: Present only the documented image-model card metrics with scope and limitations.
11. **Current Limitations**: Clinical validation, privacy, security, streaming, performance-evaluation repairs.
12. **Future Work**: Validated evaluation, secure production deployment, robust batch jobs, model monitoring, clinical studies.

### Recommended visual assets

- Product logo from `frontend/public/cardiosense-ai-logo.png`.
- One screenshot of signal upload/result output.
- One screenshot of image result with Grad-CAM.
- One dashboard or analytics screenshot.
- A simplified editable architecture diagram.
- A sample waveform from the PTB-XL sample data.

### Presentation rule

Present model output as an **AI-generated assessment**. Do not present it as medical diagnosis, clinical proof, or validated patient-risk prediction.

---

## 18. Key Source Files

| File | Why it matters |
|---|---|
| `README.md` | Product summary, features, setup, safety positioning |
| `MODEL_INTEGRATION.md` | Verified integration notes for both model pipelines |
| `backend/app/main.py` | Service startup, model loading, and routes |
| `backend/app/services/ecg_service.py` | Signal file processing and result assembly |
| `backend/app/ml/predictor.py` | Signal inference and threshold logic |
| `backend/app/ml/preprocessing.py` | Filter and normalization pipeline |
| `backend/app/ml/image_predictor.py` | Image preprocessing and inference |
| `backend/app/ml/image_interpretation.py` | Image class labels and grouped assessment |
| `backend/app/services/model_evaluation.py` | Performance-evaluation implementation and issues |
| `ecg-image-model/MODEL_CARD.md` | Image-model dataset, metrics, and limitations |
| `frontend/src/App.jsx` | Application route map |
| `frontend/src/services/api.js` | Frontend API integration |
| `docker-compose.yml` | Container deployment structure |

---

## 19. Final Positioning Statement

CardioSense AI is a well-scoped research platform that demonstrates how dual-mode ECG AI, explainability, reporting, and web application design can be combined. Its strongest qualities are the use of two real model checkpoints, explicit separation of signal and image workflows, and attention to user-facing explanation and safety language. The next phase should focus on evaluation correctness, data security, operational durability, and clinical validation before any real-world healthcare deployment.
