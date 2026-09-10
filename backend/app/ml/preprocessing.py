import numpy as np
from scipy.signal import butter, filtfilt
from typing import Tuple
import json
from pathlib import Path

from app.core.config import settings


def load_preprocessing_config() -> dict:
    with open(settings.MODEL_CONFIG_PATH, "r") as f:
        config = json.load(f)
    return config.get("preprocessing", {})


PREPROCESSING_CONFIG = load_preprocessing_config()
BANDPASS_LOW = PREPROCESSING_CONFIG.get("bandpass_lowcut", 0.5)
BANDPASS_HIGH = PREPROCESSING_CONFIG.get("bandpass_highcut", 40.0)
BANDPASS_ORDER = PREPROCESSING_CONFIG.get("bandpass_order", 4)
SAMPLING_RATE = 100
NORMALIZATION = PREPROCESSING_CONFIG.get("normalization", "per_record_zscore")


def bandpass_filter(
    signal: np.ndarray,
    lowcut: float = BANDPASS_LOW,
    highcut: float = BANDPASS_HIGH,
    fs: int = SAMPLING_RATE,
    order: int = BANDPASS_ORDER
) -> np.ndarray:
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype="band")
    return filtfilt(b, a, signal, axis=0)


def preprocess_signal(signal: np.ndarray) -> np.ndarray:
    if signal.shape[0] == 12 and signal.shape[1] != 12:
        signal = signal.T
    
    signal = bandpass_filter(signal, fs=SAMPLING_RATE)
    
    mean = signal.mean(axis=0, keepdims=True)
    std = signal.std(axis=0, keepdims=True) + 1e-8
    signal = (signal - mean) / std
    
    return signal.T.astype(np.float32)


def validate_signal(signal: np.ndarray, expected_leads: int = 12, expected_length: int = 1000) -> Tuple[bool, str]:
    if signal.size == 0:
        return False, "Empty signal"
    
    if signal.ndim != 2:
        return False, f"Signal must be 2D, got {signal.ndim}D"
    
    if signal.shape[0] == expected_leads and signal.shape[1] == expected_length:
        pass
    elif signal.shape[1] == expected_leads and signal.shape[0] == expected_length:
        pass
    else:
        return False, f"Expected shape ({expected_leads}, {expected_length}) or ({expected_length}, {expected_leads}), got {signal.shape}"
    
    if np.isnan(signal).any() or np.isinf(signal).any():
        return False, "Signal contains NaN or Inf values"
    
    if np.all(signal == 0):
        return False, "Signal is all zeros"
    
    return True, "Valid"


def signal_to_tensor(signal: np.ndarray) -> "torch.Tensor":
    import torch
    processed = preprocess_signal(signal)
    tensor = torch.tensor(processed, dtype=torch.float32).unsqueeze(0)
    return tensor