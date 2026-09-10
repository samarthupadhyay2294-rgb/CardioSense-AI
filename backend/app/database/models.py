from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.database.database import Base


class ECGAnalysis(Base):
    __tablename__ = "ecg_analyses"

    id = Column(Integer, primary_key=True, index=True)
    analysis_type = Column(String(20), nullable=False, default="signal")
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=True)
    prediction = Column(String(100), nullable=False)
    prediction_code = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False)
    probabilities = Column(JSON, nullable=False)
    all_predictions = Column(JSON, nullable=True)
    signal_quality = Column(String(50), nullable=True)
    sampling_rate = Column(Integer, nullable=True)
    duration = Column(Float, nullable=True)
    num_leads = Column(Integer, nullable=True)
    model_name = Column(String(100), nullable=True)
    model_version = Column(String(50), nullable=False)
    processing_time = Column(Float, nullable=True)
    explainability = Column(JSON, nullable=True)
    ecg_statistics = Column(JSON, nullable=True)
    signal_data = Column(JSON, nullable=True)
    image_path = Column(String(500), nullable=True)
    gradcam_path = Column(String(500), nullable=True)
    gradcam_available = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "analysis_type": self.analysis_type,
            "file_name": self.file_name,
            "prediction": self.prediction,
            "prediction_code": self.prediction_code,
            "confidence": self.confidence,
            "probabilities": self.probabilities,
            "all_predictions": self.all_predictions,
            "signal_quality": self.signal_quality,
            "sampling_rate": self.sampling_rate,
            "duration": self.duration,
            "num_leads": self.num_leads,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "processing_time": self.processing_time,
            "explainability": self.explainability,
            "ecg_statistics": self.ecg_statistics,
            "signal_data": self.signal_data,
            "image_path": self.image_path,
            "gradcam_path": self.gradcam_path,
            "gradcam_available": self.gradcam_available,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "primary_prediction": getattr(self, "primary_prediction", None),
            "primary_label": getattr(self, "primary_label", None),
            "primary_confidence": getattr(self, "primary_confidence", None),
            "dominant_group": getattr(self, "dominant_group", None),
            "group_probabilities": getattr(self, "group_probabilities", None),
            "subclass_results": getattr(self, "subclass_results", None),
            "pattern_summary": getattr(self, "pattern_summary", None),
            "recommended_next_steps": getattr(self, "recommended_next_steps", None),
            "next_steps": getattr(self, "recommended_next_steps", None) or getattr(self, "next_steps", None),
            "medical_disclaimer": getattr(self, "medical_disclaimer", None),
            "distribution_verified": getattr(self, "distribution_verified", None),
            "distribution_total": getattr(self, "distribution_total", None),
        }
