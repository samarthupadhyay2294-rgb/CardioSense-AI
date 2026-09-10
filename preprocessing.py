
import numpy as np
from scipy.signal import butter, filtfilt

def bandpass_filter(signal, lowcut=0.5, highcut=40.0, fs=100, order=4):
    nyq = 0.5 * fs
    b, a = butter(order, [lowcut/nyq, highcut/nyq], btype="band")
    return filtfilt(b, a, signal, axis=0)

def preprocess_signal(signal):
    if signal.shape[0] == 12 and signal.shape[1] != 12:
        signal = signal.T
    signal = bandpass_filter(signal, fs=100)
    mean = signal.mean(axis=0, keepdims=True)
    std = signal.std(axis=0, keepdims=True) + 1e-8
    signal = (signal - mean) / std
    return signal.T.astype(np.float32)
