<div align="center">

# 🫀 CardioSense AI

### *Intelligent ECG Analysis. Clearer Cardiac Insights.*

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://react.dev)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.1%2B-red.svg)](https://pytorch.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**A full-stack healthcare AI platform that analyzes ECG signals and ECG images using two real, already-trained PyTorch deep learning models — no fabricated predictions, metrics, or statistics, ever.**

[FastAPI](https://fastapi.tiangolo.com) · [PyTorch](https://pytorch.org) · [React](https://react.dev) · [Vite](https://vitejs.dev) · [Tailwind CSS](https://tailwindcss.com) · [SQLAlchemy](https://www.sqlalchemy.org) · [ReportLab](https://www.reportlab.com)

---

⚠️ **Educational / research tool. NOT a medical diagnosis.** See the [Medical Disclaimer](#️-medical-disclaimer) below.

</div>

---

## 📖 Table of Contents

- [✨ Features](#-features)
- [🎯 What Is It?](#-what-is-it)
- [🧠 The Two Real Models](#-the-two-real-models)
- [🧩 ECG Image Pattern Assessment](#-ecg-image-pattern-assessment)
- [🏗 Architecture](#-architecture)
- [📂 Repository Structure](#-repository-structure)
- [🚀 Quick Start](#-quick-start)
- [⚙ Configuration](#-configuration)
- [🐳 Docker Deployment](#-docker-deployment)
- [🖥 Using the App](#-using-the-app)
- [🔌 API Documentation](#-api-documentation)
- [🧪 Testing](#-testing)
- [🛠 Troubleshooting](#-troubleshooting)
- [🔒 Security](#-security)
- [🌍 Deployment](#-deployment)
- [🤝 Contributing](#-contributing)
- [📈 Roadmap](#-roadmap)
- [⚠️ Medical Disclaimer](#️-medical-disclaimer)
- [📄 License](#-license)

---

## ✨ Features

### 🩺 Signal Analysis
- 📤 **Multi-format Support**: Upload 12-lead ECGs in WFDB, MAT, CSV, NPY, or TXT formats
- 🧠 **Real Multi-label Inference**: 5-class classification (NORM, MI, STTC, CD, HYP) with per-class thresholds
- 📊 **Interactive Waveform Viewer**: Zoom, pan, reset, hover inspection, and lead selector
- 🔍 **Integrated Gradients**: Lead and time importance explainability
- 📈 **Signal Statistics**: Amplitude, duration, quality metrics, and sampling rate analysis

### 🖼️ Image Analysis
- 📸 **Smart Image Upload**: Instant preview with validation (type, size, decodability checks)
- 🎯 **Real EfficientNet-B0 Inference**: Exact 15-class probabilities, confidence scores, and argmax prediction
- 🔥 **Real Grad-CAM**: Heatmap overlay showing influential image regions (graceful degradation)
- 🏷️ **Human-Readable Labels**: 15 beat subclasses with ECG group aggregation
- 📋 **Dynamic Recommendations**: Pattern assessment based on actual predicted subclass
- 🛡️ **Safety Guidance**: Confidence assessment, limitations, and emergency notices

### 💻 Workspace & UX
- 🔄 **Unified Interface**: Seamless switching between signal and image analysis modes
- 📜 **Rich History**: Searchable, filterable, sortable analysis history with type filtering
- 📊 **Live Analytics Dashboard**: Real-time statistics and prediction distributions
- 🤖 **CardioSense Assistant**: AI-powered Q&A using only your analysis data
- 📄 **PDF Reports**: Professional reports for both signal and image analyses
- 🌙 **Modern UI**: Dark mode, responsive design, accessibility features, and smooth animations

---

## 🎯 What Is It?

CardioSense AI is a complete **ECG analysis web application** built for research, learning, and decision support. Users upload **ECG signals** (12-lead recordings) **or ECG images** (screenshots or photo-readings of paper ECGs) and receive real model predictions, probabilities, explainability, PDF reports, and plain-language summaries.

### 🔄 Dual Analysis Pipelines

The two analysis pipelines are **fully independent** — they share the UI, database, and statistics, but never interact at the model level:

| Feature | ECG **Signal** | ECG **Image** |
|---------|---------------|---------------|
| **Input** | WFDB `.hea`+`.dat`, `.mat`, `.csv`, `.npy`, `.txt` | PNG, JPG, JPEG (≤ 20 MB) |
| **Model** | 1-D CNN (ECGCNN) on PTB-XL | EfficientNet-B0 (transfer-learned, 15 classes) |
| **Output** | 5-class multi-label (NORM, MI, STTC, CD, HYP) | 15-beat-subclass softmax |
| **Explainability** | Integrated Gradients (lead + time) | Grad-CAM heatmap overlay |
| **Report** | Signal PDF report | Image PDF report + pattern assessment |

> 🎯 **Design principle**: Predictions come **only** from the real loaded checkpoints. Nothing is hardcoded, randomized, or fabricated — probabilities, confidence, statistics, gradient attributions, and Grad-CAM maps are all computed live from the actual trained weights.

---

## 🧠 The Two Real Models

Both models are loaded **once at application startup** and used as-is. They are **not retrained, modified, or reimplemented** — the integration code reuses the original pipelines.

### 1️⃣ ECG Signal Model — ECGCNN

| Property | Value |
|----------|-------|
| **Checkpoint** | `backend/models/ptbxl_cnn_best.pt` |
| **Architecture** | 1-D CNN (4 conv blocks, ~339K params), **no** Transformer/attention |
| **Input** | `(12, 1000)` — 12 leads × 1000 samples @ 100 Hz (10 s) |
| **Output** | 5 logits → sigmoid, per-class thresholds (multi-label) |
| **Classes** | `NORM, MI, STTC, CD, HYP` |
| **Preprocessing** | Butterworth bandpass (0.5–40 Hz, order 4) + per-record z-score |
| **Explainability** | **Integrated Gradients** (lead_importance, time_importance) |

### 2️⃣ ECG Image Model — EfficientNet-B0

| Property | Value |
|----------|-------|
| **Checkpoint** | `backend/models/image/best_model.pt` |
| **Architecture** | torchvision `efficientnet_b0(weights=None)`, classifier → `Linear(…, 15)` |
| **Input** | RGB → Resize 244 → CenterCrop 224 → ImageNet normalize |
| **Output** | 15-class softmax; prediction = argmax |
| **Classes** | `A E F J L N Q R S V aa e f j p` (see pattern assessment table below) |
| **Preprocessing** | Reuses `ecg-image-model/src/transforms.py` (training-compatible, untouched) |
| **Explainability** | **Grad-CAM** on `model.features[-1]` |

> 📚 Both integrate with the real metric/config data (`backend/config/model_config.json` and `backend/models/image/model_config.json`). See [`MODEL_INTEGRATION.md`](MODEL_INTEGRATION.md) for detailed integration documentation.

---

## 🧩 ECG Image Pattern Assessment

On top of the raw 15-class output, the app derives a deterministic, human-readable pattern assessment — **no extra model, no retraining** — implemented in `backend/app/ml/image_interpretation.py`.

### 📋 All 15 Subclasses (Human-Readable Labels)

| Code | Subclass | ECG Group |
|------|----------|-----------|
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

### 🔍 Analysis Process (Web + PDF)

1. **Predicted Class** — Shown as the human-readable subclass (e.g., "*Unclassifiable Beat*")
2. **All 15 Subclass Probabilities** — Sorted highest → lowest, exact model percentages, human labels only (raw codes stay internal)
3. **ECG Pattern Group Summary** — Five aggregated group probabilities:
   - Normal = `N+L+R+e+j`
   - Supraventricular = `A+J+S+aa`
   - Ventricular = `V+E`
   - Fusion = `F`
   - Other/Unclassifiable = `Q+p+f`
4. **ECG Pattern Report** — Interpretation based on the *complete* distribution (dominant pattern, strongest group, confidence assessment, abnormal-pattern note, professional-review flag)
5. **Recommended Next Steps** — Generated **dynamically from the actual predicted subclass**, never from hardcoded examples. Includes uncertainty notes when confidence is low and emergency-safety notices
6. **Confidence & Limitations** + **Medical Disclaimer**

> 🔒 Raw class codes are stored in the backend but **never displayed** as user-facing predictions or probability labels on the web page or PDF.

---

## 🏗 Architecture

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────────────────────────────┐
│         FastAPI (uvicorn :8000)      │
├─────────────────────────────────────┤
│ ├─ /api/ecg/*          signal pipeline │
│ ├─ /api/ecg-image/*    image pipeline │
│ ├─ /api/history        paged + filtered │
│ ├─ /api/statistics     live aggregations│
│ ├─ /api/model/*        model info/status│
│ └─ SQLite / PostgreSQL storage       │
└─────────────────────────────────────┘
```

### 🛠️ Technology Stack

- **Frontend**: React 18 + Vite 6 + Tailwind CSS 3 + React Router + Framer Motion + Plotly/Recharts
- **Backend**: FastAPI + SQLAlchemy 2 + PyTorch + ReportLab
- **Database**: SQLite (default) / PostgreSQL (production)
- **ML Framework**: PyTorch with CUDA support
- **PDF Generation**: ReportLab
- **API Documentation**: Swagger UI (automatic)

See [`docs/architecture.md`](docs/architecture.md) for detailed data-flow diagrams and design rules.

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

## 🚀 Quick Start

### 📋 Prerequisites

- **Python 3.11+** (tested with 3.14) and `pip`
- **Node.js 18+** and npm
- PostgreSQL (optional, for production storage; SQLite is default)

### 1️⃣ Backend Setup

```bash
cd backend
py -3 -m pip install -r requirements.txt
copy .env.example .env      # adjust paths if needed
py -3 -m uvicorn app.main:app --reload --port 8000
```

**Verification**: Open **http://localhost:8000/docs** (Swagger UI) and check **GET /api/health** returns:
```json
{
  "status": "ok",
  "model_loaded": true,
  "image_model_loaded": true,
  ...
}
```

> 💡 **Windows Users**: Use `py -3` instead of `python3` and `npm.cmd` instead of `npm`

### 2️⃣ Frontend Setup

```bash
cd frontend
npm install
npm run dev                 # http://localhost:5173
```

The Vite dev server automatically proxies `/api` → `http://localhost:8000`.

### 🎉 Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

---

## ⚙ Configuration

All settings come from environment variables (see `backend/.env.example`):

| Variable | Default | Purpose |
|----------|---------|---------|
| `SIGNAL_MODEL_PATH` | `models/ptbxl_cnn_best.pt` | Signal checkpoint path |
| `IMAGE_MODEL_PATH` | `models/image/best_model.pt` | Image checkpoint path |
| `IMAGE_MODEL_CONFIG` | `models/image/model_config.json` | Image config (classes, normalization) |
| `ENABLE_IMAGE_MODEL` | `true` | Set `false` to disable the image pipeline entirely |
| `DATABASE_URL` | `sqlite:///./cardiosense.db` | Storage connection string |
| `CORS_ORIGINS` | `["http://localhost:5173"]` | Allowed frontend origins |
| `MAX_UPLOAD_SIZE_MB` | `20` | Max image upload size |
| `MODEL_VERSION` | `1.0` | Version reported by the API |
| `ENVIRONMENT` | `development` | `development` → debug logging |

---

## 🐳 Docker Deployment

### 🚀 Quick Docker Start

```bash
docker compose up --build
```

### 🌐 Access Points

- **Frontend**: http://localhost:5173
- **Backend**: http://localhost:8000
- **Database**: PostgreSQL on port 5432

### 📋 Docker Services

- **backend**: FastAPI application with model loading
- **frontend**: React application with Vite
- **db**: PostgreSQL database

---

## 🖥 Using the App

### 📤 Step-by-Step Guide

1. **Open Application**: Navigate to **http://localhost:5173** and click **Analyze ECG**
2. **Choose Analysis Type**: Select **ECG Signal** or **ECG Image** using the mode selector
3. **Upload Your Data**:
   - **Signal**: Upload a 12-lead ECG. A sample pair is available at `data/sample_ecg/00001_lr.hea` + `.dat` (normal) — upload both files together
   - **Image**: Upload a PNG/JPG/JPEG of an ECG (≤ 20 MB); preview is shown before analysis
4. **View Results**:
   - **Signal**: ECG waveform, statistics, Integrated Gradients explainability
   - **Image**: Uploaded image, real Grad-CAM overlay, ECG Pattern Assessment (subclass labels, group bars, report, next steps, confidence & limitations)
5. **Export & Interact**:
   - Download a **PDF report**
   - Ask the **Assistant** questions about the analysis
6. **Track & Analyze**:
   - Monitor everything on **Dashboard**
   - Review **History** (with Signal/Image filter)
   - Explore **Analytics** (separate signal and image prediction distributions)

### 🎯 Key Features

- **🔄 Real-time Analysis**: Get instant predictions from pre-trained models
- **📊 Interactive Visualizations**: Explore waveforms and probability distributions
- **🔍 Explainability**: Understand model decisions with Integrated Gradients and Grad-CAM
- **📱 Responsive Design**: Works seamlessly on desktop and mobile devices
- **🌙 Dark Mode**: Easy on the eyes for extended use

---

## 🔌 API Documentation

### 📋 Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Service + model health check |
| `POST` | `/api/ecg/analyze` | Analyze an ECG signal |
| `GET` | `/api/ecg/{id}` | Fetch a signal analysis |
| `GET` | `/api/ecg/report/{id}` | Generate signal PDF report |
| `POST` | `/api/ecg/{id}/summary` | Generate plain-language signal summary |
| `POST` | `/api/ecg/{id}/assistant` | Ask the assistant about a signal |
| `POST` | `/api/ecg-image/analyze` | Analyze an ECG image |
| `GET` | `/api/ecg-image/{id}` | Fetch an image analysis (enriched interpretation) |
| `GET` | `/api/ecg-image/{id}/image` | Retrieve stored uploaded image (PNG) |
| `GET` | `/api/ecg-image/{id}/gradcam` | Retrieve stored Grad-CAM overlay (PNG) |
| `GET` | `/api/ecg-image/report/{id}` | Generate image PDF report (incl. pattern assessment) |
| `POST` | `/api/ecg-image/{id}/summary` | Generate image summary |
| `POST` | `/api/ecg-image/{id}/assistant` | Ask the assistant about an image |
| `GET` | `/api/history` | Get paginated analysis history |
| `GET` | `/api/statistics` | Get live analytics and aggregations |
| `GET` | `/api/model/info` | Get signal model information |
| `GET` | `/api/model/image-info` | Get image model information |
| `GET` | `/api/model/status` | Get model loading status |

### 📚 Full Documentation

- **Interactive API Docs**: http://localhost:8000/docs (Swagger UI)
- **Detailed API Reference**: [`docs/api.md`](docs/api.md)
- **Architecture Details**: [`docs/architecture.md`](docs/architecture.md)
- **Model Documentation**: [`docs/model.md`](docs/model.md)

---

## 🧪 Testing

### 🧪 Run Test Suite

```bash
cd backend
py -3 -m pytest tests -v
```

### 📊 Test Coverage

The comprehensive test suite (32 tests) covers:
- ✅ Health endpoints and model status
- ✅ Both model loaders (signal and image)
- ✅ Preprocessing shapes and validation
- ✅ Prediction output verification
- ✅ Image upload endpoints and validation
- ✅ Grad-CAM generation and fallback
- ✅ Interpretation (label mapping + group aggregation)
- ✅ Distribution verification
- ✅ Report field validation
- ✅ History and pagination
- ✅ Database behavior and migrations

### 🎯 Test Categories

- **API Tests**: Endpoint functionality, error handling, response validation
- **ML Tests**: Model loading, preprocessing, prediction accuracy
- **Integration Tests**: End-to-end workflows, database operations
- **Validation Tests**: Input validation, file upload checks

---

## 🛠 Troubleshooting

### 🔧 Common Issues

| Issue | Solution |
|-------|----------|
| **Port already in use** | Change `--port` for uvicorn and update Vite proxy / `VITE_API_BASE_URL` |
| **Signal model not loading** | Confirm `SIGNAL_MODEL_PATH` → `ptbxl_cnn_best.pt` and torch is installed. Check `/api/model/status` |
| **Image model not loading** | Confirm `IMAGE_MODEL_PATH`/`IMAGE_MODEL_CONFIG` and `ENABLE_IMAGE_MODEL=true`. Signal pipeline still works (`image_model.loaded: false`) |
| **CORS errors** | Make sure `CORS_ORIGINS` includes your frontend origin (e.g., `http://localhost:5173`) |
| **Windows blocks `npm`** | Use `npm.cmd` instead of `npm` |
| **PDF download fails** | Check `backend/reports/` is writable and ReportLab is installed |
| **Database errors** | Verify `DATABASE_URL` is correct and database is accessible |
| **Memory issues** | Reduce batch size or use a machine with more RAM for large model operations |

### 🐛 Debug Mode

Enable debug logging by setting:
```bash
ENVIRONMENT=development
```

This provides detailed logging for troubleshooting.

---

## 🔒 Security

### 🛡️ Security Features

- **Model Protection**: Model checkpoints are read from disk only; they are **never** exposed through API routes
- **Upload Validation**: Files are validated by extension, MIME type, size, and decodability
- **Secret Management**: Production secrets come from environment variables — never commit real `.env` values
- **Error Handling**: Errors are logged in detail server-side but shown generically to users
- **CORS Protection**: Configurable CORS origins to prevent unauthorized access
- **Input Sanitization**: All user inputs are validated and sanitized

### 🔐 Best Practices

- Never commit `.env` files or real credentials
- Use strong passwords for production databases
- Keep dependencies updated
- Use HTTPS in production
- Implement rate limiting for API endpoints
- Regular security audits

---

## 🌍 Deployment

### 🚀 Production Deployment

#### Database Setup
```bash
# Use PostgreSQL for production
DATABASE_URL=postgresql://user:password@host:5432/database
```

#### Frontend Build
```bash
cd frontend
npm run build
# Serve dist/ behind a static server (nginx, Apache, etc.)
```

#### Backend Deployment
```bash
# Run uvicorn behind a reverse proxy
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Docker Deployment
```bash
docker compose -f docker-compose.yml up -d
```

### 📋 Deployment Checklist

- [ ] Set `ENVIRONMENT=production`
- [ ] Configure PostgreSQL database
- [ ] Set strong database passwords
- [ ] Configure CORS origins for production domain
- [ ] Enable HTTPS/SSL
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy
- [ ] Deploy model checkpoints with the application
- [ ] Test all endpoints in production environment
- [ ] Set up error tracking (e.g., Sentry)

### 🌐 Cloud Deployment

The application can be deployed to:
- **AWS**: EC2, ECS, or Lambda
- **Google Cloud**: Compute Engine, Cloud Run
- **Azure**: App Service, Container Instances
- **Heroku**: With appropriate buildpacks
- **DigitalOcean**: App Platform or Droplets

---

## 🤝 Contributing

### 📝 How to Contribute

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### 🎯 Contribution Guidelines

- Follow the existing code style
- Write tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting
- Use descriptive commit messages
- Be respectful and constructive in code reviews

### 🐛 Bug Reports

When reporting bugs, please include:
- Description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Relevant logs or error messages

---

## 📈 Roadmap

### 🎯 Planned Features

- [ ] **Enhanced Model Support**: Add more ECG analysis models
- [ ] **Batch Processing**: Analyze multiple ECGs at once
- [ ] **Advanced Analytics**: Time-series analysis and trend detection
- [ ] **Mobile App**: Native iOS and Android applications
- [ ] **Integration**: Electronic Health Record (EHR) system integration
- [ ] **Multi-language Support**: Internationalization (i18n)
- [ ] **User Authentication**: Secure user accounts and data privacy
- [ ] **Export Options**: Additional export formats (DICOM, HL7)
- [ ] **Real-time Monitoring**: Live ECG streaming and analysis
- [ ] **Collaboration Features**: Share analyses with healthcare teams

### 🔄 Recent Improvements

- ✅ Fixed ECG image prediction display bug
- ✅ Enhanced frontend data fetching logic
- ✅ Improved test coverage and validation
- ✅ Updated documentation and API reference
- ✅ Optimized model loading and performance

---

## ⚠️ Medical Disclaimer

**CardioSense AI provides AI-generated ECG signal and image analysis for research and decision-support purposes only.**

### ⚠️ Important Warnings

- **Not a Medical Diagnosis**: This application is **not** a medical diagnosis and does not replace evaluation by a qualified healthcare professional
- **Pattern Similarity**: Model confidence values are measures of pattern similarity — they are **not** disease, risk, or outcome probabilities
- **Professional Consultation**: Always consult a clinician for any medical decision
- **Emergency Situations**: If you have serious symptoms (chest pain, severe shortness of breath, fainting, etc.), **seek urgent medical attention immediately**
- **No Treatment Decisions**: Never use this AI assessment to decide medication, dosage, treatment, or any medical procedure
- **Educational Tool**: This is designed as an educational and research tool, not a replacement for professional medical judgment

### 📋 Limitations

- Models are trained on specific datasets and may not generalize to all populations
- Image quality and format can significantly affect accuracy
- The system does not account for patient history, symptoms, or clinical context
- False positives and false negatives are possible
- Regular calibration and validation with clinical data is recommended

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### 📜 License Summary

- ✅ Commercial use allowed
- ✅ Modification allowed
- ✅ Distribution allowed
- ✅ Private use allowed
- ❌ Liability and warranty disclaimed

---

## 🙏 Acknowledgments

- **PTB-XL Dataset**: PhysioNet for the ECG signal dataset
- **MIT-BIH Arrhythmia Database**: Source for ECG image classification
- **PyTorch Team**: For the excellent deep learning framework
- **FastAPI Community**: For the modern web framework
- **React Team**: For the powerful frontend library
- **Medical AI Community**: For ongoing research and collaboration

---

## 📞 Support & Contact

### 🆘 Getting Help

- **Documentation**: Check the [`docs/`](docs/) folder for detailed guides
- **Issues**: Open an issue on GitHub for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Email**: For commercial inquiries or support

### 🔗 Resources

- **GitHub Repository**: [CardioSense-AI](https://github.com/samarthupadhyay2294-rgb/CardioSense-AI)
- **API Documentation**: http://localhost:8000/docs
- **Model Integration**: [`MODEL_INTEGRATION.md`](MODEL_INTEGRATION.md)
- **Architecture Guide**: [`docs/architecture.md`](docs/architecture.md)

---

<div align="center">

**Built with ❤️ for better cardiac healthcare**

**[⬆ Back to Top](#-cardiosense-ai)**

</div>
