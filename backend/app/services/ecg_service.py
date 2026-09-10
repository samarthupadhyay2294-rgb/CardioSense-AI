import numpy as np
import wfdb
import os
import tempfile
import json
from typing import Tuple, Dict, Any, Optional
from pathlib import Path

from app.core.config import settings
from app.ml.predictor import predictor
from app.ml.explainability import explainability_engine
from app.ml.preprocessing import validate_signal, preprocess_signal


SUPPORTED_EXTENSIONS = {".dat", ".hea", ".mat", ".csv", ".npy", ".txt"}
MAX_FILE_SIZE = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
EXPECTED_LEADS = 12
EXPECTED_LENGTH = 1000
EXPECTED_SAMPLING_RATE = 100


def read_ecg_file(file_path: str) -> Tuple[np.ndarray, Dict[str, Any]]:
    ext = Path(file_path).suffix.lower()
    
    metadata = {
        "sampling_rate": EXPECTED_SAMPLING_RATE,
        "num_leads": EXPECTED_LEADS,
        "duration": EXPECTED_LENGTH / EXPECTED_SAMPLING_RATE
    }
    
    if ext in [".dat", ".hea"]:
        base_path = file_path.replace(".dat", "").replace(".hea", "")
        record = wfdb.rdrecord(base_path)
        signal = record.p_signal
        metadata["sampling_rate"] = record.fs
        metadata["num_leads"] = record.n_sig
        metadata["duration"] = record.sig_len / record.fs if record.fs > 0 else 0
    elif ext == ".mat":
        import scipy.io
        data = scipy.io.loadmat(file_path)
        signal = None
        for key in data.keys():
            if not key.startswith("__"):
                signal = data[key]
                break
        if signal is None:
            raise ValueError("No valid signal found in .mat file")
    elif ext == ".csv":
        signal = np.loadtxt(file_path, delimiter=",")
    elif ext == ".npy":
        signal = np.load(file_path)
    elif ext == ".txt":
        signal = np.loadtxt(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")
    
    signal = np.array(signal, dtype=np.float32)
    
    if signal.ndim == 1:
        signal = signal.reshape(-1, 1)
    
    return signal, metadata


def validate_ecg_signal(signal: np.ndarray, metadata: Dict) -> Tuple[bool, str]:
    is_valid, msg = validate_signal(signal, EXPECTED_LEADS, EXPECTED_LENGTH)
    if not is_valid:
        return False, msg
    
    sr = metadata.get("sampling_rate", EXPECTED_SAMPLING_RATE)
    if sr != EXPECTED_SAMPLING_RATE:
        return False, f"Sampling rate must be {EXPECTED_SAMPLING_RATE} Hz, got {sr} Hz"
    
    num_leads = metadata.get("num_leads", signal.shape[0] if signal.shape[0] == 12 else signal.shape[1])
    if num_leads != EXPECTED_LEADS:
        return False, f"Expected {EXPECTED_LEADS} leads, got {num_leads}"
    
    return True, "Valid"


def downsample_signal(signal: np.ndarray, target_points: int = 1000) -> list:
    num_points = signal.shape[1]
    if num_points <= target_points:
        return [[round(float(v), 6) for v in lead] for lead in signal]
    indices = np.linspace(0, num_points - 1, target_points).astype(int)
    return [[round(float(signal[lead, i]), 6) for i in indices] for lead in range(signal.shape[0])]


def compute_signal_quality(signal: np.ndarray) -> str:
    if signal.size == 0:
        return "poor"
    
    snr_estimate = np.std(signal) / (np.mean(np.abs(signal)) + 1e-8)
    
    if snr_estimate > 3:
        return "excellent"
    elif snr_estimate > 1.5:
        return "good"
    elif snr_estimate > 0.5:
        return "fair"
    else:
        return "poor"


def compute_ecg_statistics(signal: np.ndarray) -> Dict[str, Any]:
    stats = {}
    lead_names = ["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"]
    
    for i, lead in enumerate(lead_names):
        if i < signal.shape[0]:
            lead_signal = signal[i]
            stats[lead] = {
                "mean": float(np.mean(lead_signal)),
                "std": float(np.std(lead_signal)),
                "min": float(np.min(lead_signal)),
                "max": float(np.max(lead_signal)),
                "rms": float(np.sqrt(np.mean(lead_signal**2)))
            }
    
    stats["overall"] = {
        "mean_amplitude": float(np.mean(np.abs(signal))),
        "max_amplitude": float(np.max(np.abs(signal))),
        "signal_length": int(signal.shape[1]),
        "num_leads": int(signal.shape[0])
    }
    
    return stats


async def process_ecg_file(file_path: str, file_name: str) -> Dict[str, Any]:
    signal, metadata = read_ecg_file(file_path)
    
    is_valid, msg = validate_ecg_signal(signal, metadata)
    if not is_valid:
        raise ValueError(f"Signal validation failed: {msg}")
    
    if signal.shape[0] == EXPECTED_LENGTH and signal.shape[1] == EXPECTED_LEADS:
        signal = signal.T
    
    original_signal = signal.copy()
    
    if signal.shape[1] != EXPECTED_LENGTH:
        from scipy.signal import resample
        signal = resample(signal, EXPECTED_LENGTH, axis=1)
        original_signal = signal.copy()
    
    prediction_result = predictor.predict(signal)
    
    signal_quality = compute_signal_quality(signal)
    ecg_statistics = compute_ecg_statistics(signal)
    
    explainability = None
    if prediction_result["prediction_code"] != "NORM":
        try:
            explainability = explainability_engine.get_attribution(
                signal, 
                prediction_result["prediction_code"],
                method="integrated_gradients"
            )
        except Exception as e:
            explainability = {"error": str(e)}
    
    signal_data = downsample_signal(original_signal, target_points=500)
    
    return {
        "file_name": file_name,
        "file_path": file_path,
        "signal_data": signal_data,
        "prediction": prediction_result["prediction"],
        "prediction_code": prediction_result["prediction_code"],
        "confidence": prediction_result["confidence"],
        "probabilities": prediction_result["probabilities"],
        "all_predictions": prediction_result["all_predictions"],
        "signal_quality": signal_quality,
        "sampling_rate": metadata.get("sampling_rate", EXPECTED_SAMPLING_RATE),
        "duration": metadata.get("duration", EXPECTED_LENGTH / EXPECTED_SAMPLING_RATE),
        "num_leads": metadata.get("num_leads", EXPECTED_LEADS),
        "model_version": prediction_result["model_version"],
        "processing_time": prediction_result["processing_time"],
        "explainability": explainability,
        "ecg_statistics": ecg_statistics
    }


def save_uploaded_file(file_content: bytes, filename: str) -> str:
    upload_dir = Path(settings.MODEL_PATH).parent.parent / "uploads"
    upload_dir.mkdir(exist_ok=True)
    
    safe_filename = "".join(c for c in filename if c.isalnum() or c in "._-")
    file_path = upload_dir / safe_filename
    
    counter = 1
    original_path = file_path
    while file_path.exists():
        stem = original_path.stem
        suffix = original_path.suffix
        file_path = upload_dir / f"{stem}_{counter}{suffix}"
        counter += 1
    
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    return str(file_path)