import numpy as np
from scipy import signal
from scipy.fft import fft, fftfreq
from typing import Dict, List


class ECGFeatureExtractor:
    """
    Extract clinically relevant ECG features.
    
    NOTE: These are estimated signal features, not clinically validated measurements.
    Where accurate clinical delineation algorithms are not available, 
    measurements are marked as estimated signal features.
    """
    
    def __init__(self, sampling_rate: int = 100):
        self.sampling_rate = sampling_rate
        self.lead_names = ["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"]
    
    def detect_r_peaks(self, lead_signal: np.ndarray) -> np.ndarray:
        """
        Detect R peaks using basic peak detection.
        
        NOTE: This is an estimated signal feature, not a clinically validated method.
        """
        from scipy.signal import find_peaks
        # Basic peak detection - not clinically validated
        peaks, _ = find_peaks(lead_signal, height=0.3, distance=20)
        return peaks
    
    def extract_rr_intervals(self, r_peaks: np.ndarray) -> List[float]:
        """Calculate RR intervals in seconds."""
        if len(r_peaks) < 2:
            return []
        
        rr_samples = np.diff(r_peaks)
        rr_seconds = rr_samples / self.sampling_rate
        return rr_seconds.tolist()
    
    def calculate_heart_rate(self, rr_intervals: List[float]) -> Dict[str, float]:
        """Calculate heart rate statistics from RR intervals."""
        if not rr_intervals:
            return {"mean": 0, "min": 0, "max": 0, "std": 0, "current": 0}
        
        heart_rates = [60.0 / rr for rr in rr_intervals]
        
        return {
            "mean": float(np.mean(heart_rates)),
            "min": float(np.min(heart_rates)),
            "max": float(np.max(heart_rates)),
            "std": float(np.std(heart_rates)),
            "current": float(heart_rates[-1]) if heart_rates else 0
        }
    
    def extract_qrs_features(self, lead_signal: np.ndarray, r_peaks: np.ndarray) -> Dict[str, float]:
        """
        Extract QRS complex features.
        
        NOTE: These are estimated signal features, not clinically validated measurements.
        """
        if len(r_peaks) == 0:
            return {"duration": 0, "amplitude": 0, "estimated": True}
        
        # Analyze first QRS complex
        r_peak = r_peaks[0]
        window = 20  # samples
        qrs_window = lead_signal[max(0, r_peak-window):min(len(lead_signal), r_peak+window)]
        
        if len(qrs_window) == 0:
            return {"duration": 0, "amplitude": 0, "estimated": True}
        
        # Simple QRS duration estimation
        qrs_duration = 0.08  # Default estimation in seconds
        qrs_amplitude = np.max(qrs_window) - np.min(qrs_window)
        
        return {
            "duration": float(qrs_duration),
            "amplitude": float(qrs_amplitude),
            "estimated": True  # Mark as estimated
        }
    
    def extract_st_segment(self, lead_signal: np.ndarray, r_peaks: np.ndarray) -> Dict[str, float]:
        """
        Extract ST segment features.
        
        NOTE: These are estimated signal features, not clinically validated measurements.
        """
        if len(r_peaks) == 0:
            return {"elevation": 0, "depression": 0, "level": 0, "estimated": True}
        
        r_peak = r_peaks[0]
        st_start = r_peak + 10  # 100ms after R peak
        st_end = r_peak + 20    # 200ms after R peak
        
        if st_end >= len(lead_signal):
            return {"elevation": 0, "depression": 0, "level": 0, "estimated": True}
        
        st_segment = lead_signal[st_start:st_end]
        st_level = np.mean(st_segment)
        
        # Baseline estimation (PR segment)
        pr_start = r_peak - 15
        pr_end = r_peak - 5
        if pr_start >= 0:
            baseline = np.mean(lead_signal[pr_start:pr_end])
            st_deviation = st_level - baseline
        else:
            st_deviation = 0
        
        return {
            "elevation": float(max(0, st_deviation)),
            "depression": float(max(0, -st_deviation)),
            "level": float(st_level),
            "estimated": True  # Mark as estimated
        }
    
    def extract_pr_interval(self, lead_signal: np.ndarray, r_peaks: np.ndarray) -> float:
        """
        Extract PR interval.
        
        NOTE: This is an estimated signal feature, not clinically validated.
        """
        if len(r_peaks) == 0:
            return 0
        
        r_peak = r_peaks[0]
        # Simplified PR interval estimation
        pr_end = r_peak - 5
        pr_start = r_peak - 20
        
        if pr_start < 0:
            return 0
        
        return float((pr_end - pr_start) / self.sampling_rate)
    
    def extract_qt_interval(self, lead_signal: np.ndarray, r_peaks: np.ndarray) -> float:
        """
        Extract QT interval.
        
        NOTE: This is an estimated signal feature, not clinically validated.
        """
        if len(r_peaks) == 0:
            return 0
        
        r_peak = r_peaks[0]
        # Simplified QT interval estimation
        qt_start = r_peak - 5
        qt_end = r_peak + 25
        
        if qt_end >= len(lead_signal):
            return 0
        
        return float((qt_end - qt_start) / self.sampling_rate)
    
    def extract_temporal_features(self, ecg_signal: np.ndarray) -> Dict[str, Dict]:
        """Extract time-domain features for all leads."""
        features = {}
        
        for i, lead_name in enumerate(self.lead_names):
            if i >= ecg_signal.shape[0]:
                continue
            
            lead_signal = ecg_signal[i]
            r_peaks = self.detect_r_peaks(lead_signal)
            rr_intervals = self.extract_rr_intervals(r_peaks)
            
            features[lead_name] = {
                "heart_rate": self.calculate_heart_rate(rr_intervals),
                "rr_intervals": rr_intervals,
                "qrs_features": self.extract_qrs_features(lead_signal, r_peaks),
                "st_segment": self.extract_st_segment(lead_signal, r_peaks),
                "pr_interval": self.extract_pr_interval(lead_signal, r_peaks),
                "qt_interval": self.extract_qt_interval(lead_signal, r_peaks)
            }
        
        return features
    
    def extract_frequency_features(self, ecg_signal: np.ndarray) -> Dict[str, Dict]:
        """Extract frequency-domain features for all leads."""
        features = {}
        
        for i, lead_name in enumerate(self.lead_names):
            if i >= ecg_signal.shape[0]:
                continue
            
            lead_signal = ecg_signal[i]
            
            # FFT
            fft_vals = fft(lead_signal)
            fft_freq = fftfreq(len(lead_signal), 1/self.sampling_rate)
            
            # Power spectrum
            power_spectrum = np.abs(fft_vals)**2
            
            # Find dominant frequency
            dominant_idx = np.argmax(power_spectrum[:len(power_spectrum)//2])
            dominant_freq = abs(fft_freq[dominant_idx])
            
            # Frequency bands (standard ECG frequency ranges)
            bands = {
                "very_low": (0, 0.5),
                "low": (0.5, 4),
                "medium": (4, 15),
                "high": (15, 40)
            }
            
            band_power = {}
            for band_name, (low, high) in bands.items():
                mask = (np.abs(fft_freq) >= low) & (np.abs(fft_freq) < high)
                band_power[band_name] = float(np.sum(power_spectrum[mask]))
            
            # Spectral entropy
            power_normalized = power_spectrum / (np.sum(power_spectrum) + 1e-10)
            spectral_entropy = -np.sum(power_normalized * np.log(power_normalized + 1e-10))
            
            features[lead_name] = {
                "dominant_frequency": float(dominant_freq),
                "band_power": band_power,
                "spectral_entropy": float(spectral_entropy),
                "total_power": float(np.sum(power_spectrum))
            }
        
        return features
    
    def extract_morphological_features(self, ecg_signal: np.ndarray) -> Dict[str, Dict]:
        """Extract morphological/statistical features for all leads."""
        features = {}
        
        for i, lead_name in enumerate(self.lead_names):
            if i >= ecg_signal.shape[0]:
                continue
            
            lead_signal = ecg_signal[i]
            
            # Statistical features
            features[lead_name] = {
                "mean": float(np.mean(lead_signal)),
                "std": float(np.std(lead_signal)),
                "skewness": float(self._skewness(lead_signal)),
                "kurtosis": float(self._kurtosis(lead_signal)),
                "zero_crossings": int(self._zero_crossings(lead_signal)),
                "rms": float(np.sqrt(np.mean(lead_signal**2)))
            }
        
        return features
    
    def _skewness(self, data: np.ndarray) -> float:
        """Calculate skewness."""
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0
        return np.mean(((data - mean) / std)**3)
    
    def _kurtosis(self, data: np.ndarray) -> float:
        """Calculate kurtosis."""
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0
        return np.mean(((data - mean) / std)**4) - 3
    
    def _zero_crossings(self, data: np.ndarray) -> int:
        """Count zero crossings."""
        return int(np.sum(np.diff(np.sign(data)) != 0))
    
    def extract_all_features(self, ecg_signal: np.ndarray) -> Dict[str, Dict]:
        """Extract all feature types (temporal, frequency, morphological)."""
        return {
            "temporal": self.extract_temporal_features(ecg_signal),
            "frequency": self.extract_frequency_features(ecg_signal),
            "morphological": self.extract_morphological_features(ecg_signal)
        }


# Global instance
feature_extractor = ECGFeatureExtractor()