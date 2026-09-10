from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, List, Optional, Any
from datetime import datetime


class SubclassProbability(BaseModel):
    raw_class: str
    human_readable_label: str
    probability: float
    group: str
    group_probability: float


class ECGAnalysisCreate(BaseModel):
    analysis_type: str = "signal"
    file_name: str
    prediction: str
    prediction_code: str
    confidence: float
    probabilities: Dict[str, float]
    all_predictions: Optional[Dict[str, bool]] = None
    signal_quality: Optional[str] = None
    sampling_rate: Optional[int] = None
    duration: Optional[float] = None
    num_leads: Optional[int] = None
    model_name: Optional[str] = None
    model_version: str
    processing_time: Optional[float] = None
    explainability: Optional[Dict[str, Any]] = None
    ecg_statistics: Optional[Dict[str, Any]] = None
    signal_data: Optional[list] = None
    image_path: Optional[str] = None
    gradcam_path: Optional[str] = None
    gradcam_available: Optional[bool] = None
    warning: Optional[str] = None


class ECGAnalysisResponse(BaseModel):
    id: int
    analysis_type: str = "signal"
    file_name: str
    prediction: str
    prediction_code: str
    confidence: float
    probabilities: Dict[str, float]
    all_predictions: Optional[Dict[str, bool]] = None
    signal_quality: Optional[str] = None
    sampling_rate: Optional[int] = None
    duration: Optional[float] = None
    num_leads: Optional[int] = None
    model_name: Optional[str] = None
    model_version: str
    processing_time: Optional[float] = None
    explainability: Optional[Dict[str, Any]] = None
    ecg_statistics: Optional[Dict[str, Any]] = None
    signal_data: Optional[list] = None
    image_path: Optional[str] = None
    gradcam_path: Optional[str] = None
    gradcam_available: Optional[bool] = None
    warning: Optional[str] = None
    distribution_verified: Optional[bool] = None
    distribution_total: Optional[float] = None
    primary_prediction: Optional[str] = None
    primary_label: Optional[str] = None
    primary_confidence: Optional[float] = None
    dominant_group: Optional[str] = None
    group_probabilities: Optional[Dict[str, float]] = None
    subclass_results: Optional[List[SubclassProbability]] = None
    pattern_summary: Optional[str] = None
    recommended_next_steps: Optional[List[str]] = None
    next_steps: Optional[List[str]] = None
    medical_disclaimer: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ECGUploadResponse(BaseModel):
    success: bool
    message: str
    analysis_id: Optional[int] = None
    prediction: Optional[Dict[str, Any]] = None


class ImageAnalysisResponse(BaseModel):
    success: bool
    message: str
    analysis_id: Optional[int] = None
    analysis_type: Optional[str] = "image"
    file_name: Optional[str] = None
    prediction: Optional[str] = None
    confidence: Optional[float] = None
    probabilities: Optional[Dict[str, float]] = None
    processing_time: Optional[float] = None
    gradcam_available: Optional[bool] = None
    warning: Optional[str] = None
    distribution_verified: Optional[bool] = None
    distribution_total: Optional[float] = None
    primary_prediction: Optional[str] = None
    primary_label: Optional[str] = None
    primary_confidence: Optional[float] = None
    dominant_group: Optional[str] = None
    group_probabilities: Optional[Dict[str, float]] = None
    subclass_results: Optional[List[SubclassProbability]] = None
    pattern_summary: Optional[str] = None
    recommended_next_steps: Optional[List[str]] = None
    next_steps: Optional[List[str]] = None
    medical_disclaimer: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    device: str
    version: str
    image_model_loaded: Optional[bool] = False


class ModelInfoResponse(BaseModel):
    model_name: str
    model_version: str
    architecture: str
    input_shape: List[int]
    sampling_rate: int
    num_leads: int
    signal_length: int
    classes: List[str]
    class_names: Dict[str, str]
    class_descriptions: Dict[str, str]
    preprocessing: Dict[str, Any]
    model_parameters: Dict[str, Any]
    thresholds: Dict[str, float]
    training_config: Dict[str, Any]
    test_metrics: Dict[str, float]


class StatisticsResponse(BaseModel):
    total_analyses: int
    normal_count: int
    abnormal_count: int
    signal_count: int = 0
    image_count: int = 0
    average_confidence: float
    prediction_distribution: Dict[str, int]
    image_prediction_distribution: Dict[str, int] = {}
    confidence_distribution: Dict[str, float]
    trend_data: List[Dict[str, Any]]
    most_common_prediction: str
    average_processing_time: float


class PaginatedResponse(BaseModel):
    items: List[ECGAnalysisResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
