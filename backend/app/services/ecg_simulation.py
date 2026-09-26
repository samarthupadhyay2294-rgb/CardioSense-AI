import numpy as np
from typing import Dict, Optional
from scipy.signal import butter, filtfilt


class ECGSimulator:
    """
    Generate realistic ECG signals for testing and educational purposes.
    
    NOTE: Mathematically generated ECG signals are NOT clinically equivalent 
    to real patient ECGs. This is for educational/research use only.
    """
    
    def __init__(self, sampling_rate: int = 100, duration: float = 10.0):
        self.sampling_rate = sampling_rate
        self.duration = duration
        self.time_points = int(sampling_rate * duration)
        self.lead_names = ["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"]
        
    def _validate_parameters(self, heart_rate: float, duration: float, noise_level: float) -> None:
        """Validate simulation parameters."""
        if not 30 <= heart_rate <= 200:
            raise ValueError(f"Heart rate must be between 30-200 BPM, got {heart_rate}")
        if not 1 <= duration <= 60:
            raise ValueError(f"Duration must be between 1-60 seconds, got {duration}")
        if not 0 <= noise_level <= 1.0:
            raise ValueError(f"Noise level must be between 0-1, got {noise_level}")
        
    def generate_p_wave(self, t: np.ndarray, amplitude: float = 0.15) -> np.ndarray:
        """Generate P wave (atrial depolarization)."""
        return amplitude * np.exp(-((t % 1.0) * 10 - 0.2)**2 / 0.005)
    
    def generate_qrs_complex(self, t: np.ndarray, amplitude: float = 1.0) -> np.ndarray:
        """Generate QRS complex (ventricular depolarization)."""
        qrs = np.zeros_like(t)
        # Q wave
        qrs -= 0.15 * amplitude * np.exp(-((t % 1.0) * 10 - 0.5)**2 / 0.0008)
        # R wave
        qrs += 0.5 * amplitude * np.exp(-((t % 1.0) * 10 - 0.52)**2 / 0.0004)
        # S wave
        qrs -= 0.1 * amplitude * np.exp(-((t % 1.0) * 10 - 0.55)**2 / 0.0006)
        return qrs
    
    def generate_t_wave(self, t: np.ndarray, amplitude: float = 0.3) -> np.ndarray:
        """Generate T wave (ventricular repolarization)."""
        return amplitude * np.exp(-((t % 1.0) * 10 - 0.8)**2 / 0.01)
    
    def generate_normal_ecg(self, heart_rate: float = 70.0) -> np.ndarray:
        """Generate normal 12-lead ECG signal."""
        self._validate_parameters(heart_rate, self.duration, 0.0)
        
        t = np.linspace(0, self.duration, self.time_points)
        heart_rate_normalized = heart_rate / 60.0
        
        # Base signal
        signal = np.zeros((12, self.time_points))
        
        # Lead-specific amplitude factors and phase shifts
        lead_factors = [1.0, 1.2, 0.5, -0.5, -0.5, 0.6, 0.8, 1.5, 1.2, 0.9, 0.7, 0.5]
        phase_shifts = [0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11]
        
        for lead in range(12):
            lead_factor = lead_factors[lead]
            phase_shift = phase_shifts[lead]
            
            ecg_signal = np.zeros_like(t)
            num_beats = int(self.duration * heart_rate_normalized)
            
            for beat in range(num_beats):
                beat_time = beat / heart_rate_normalized
                mask = (t >= beat_time) & (t < beat_time + 1.0)
                if np.any(mask):
                    t_beat = t[mask] - beat_time + phase_shift
                    ecg_signal[mask] += (
                        self.generate_p_wave(t_beat) +
                        self.generate_qrs_complex(t_beat) +
                        self.generate_t_wave(t_beat)
                    ) * lead_factor
            
            signal[lead] = ecg_signal
        
        return signal
    
    def generate_myocardial_infarction(self, heart_rate: float = 70.0) -> np.ndarray:
        """Generate ECG with MI pattern (ST elevation)."""
        signal = self.generate_normal_ecg(heart_rate)
        
        # Add ST elevation in specific leads (anterior MI pattern)
        for lead in [3, 4, 5, 8, 9]:  # aVL, aVF, V1, V2, V3
            signal[lead] += 0.2  # ST elevation
        
        # Add pathological Q waves
        t = np.linspace(0, self.duration, self.time_points)
        for lead in range(12):
            signal[lead] -= 0.1 * np.exp(-((t % 1.0) * 10 - 0.48)**2 / 0.0005)
        
        return signal
    
    def generate_sttc(self, heart_rate: float = 70.0) -> np.ndarray:
        """Generate ECG with ST/T changes."""
        signal = self.generate_normal_ecg(heart_rate)
        
        # Flatten T waves
        for lead in range(12):
            signal[lead] *= 0.7  # Reduce T wave amplitude
        
        # Add ST depression
        for lead in [1, 2, 5, 6]:  # II, III, aVF, V1
            signal[lead] -= 0.15
        
        return signal
    
    def generate_conduction_disturbance(self, heart_rate: float = 50.0) -> np.ndarray:
        """Generate ECG with conduction disturbance (bundle branch block)."""
        signal = self.generate_normal_ecg(heart_rate)
        
        # Widen QRS complex
        t = np.linspace(0, self.duration, self.time_points)
        for lead in range(12):
            qrs_mask = (t % 1.0) > 0.45
            qrs_mask &= (t % 1.0) < 0.60
            signal[lead][qrs_mask] *= 1.5  # Widen QRS
        
        return signal
    
    def generate_hypertrophy(self, heart_rate: float = 70.0) -> np.ndarray:
        """Generate ECG with ventricular hypertrophy."""
        signal = self.generate_normal_ecg(heart_rate)
        
        # Increase voltage in lateral leads
        for lead in [6, 7, 8, 9, 10, 11]:  # V1-V6
            signal[lead] *= 1.3
        
        return signal
    
    def add_noise(self, signal: np.ndarray, noise_level: float = 0.05) -> np.ndarray:
        """Add realistic noise to signal."""
        noise = np.random.normal(0, noise_level, signal.shape)
        return signal + noise
    
    def add_baseline_wander(self, signal: np.ndarray, frequency: float = 0.5) -> np.ndarray:
        """Add baseline wander."""
        t = np.linspace(0, self.duration, signal.shape[1])
        baseline = 0.1 * np.sin(2 * np.pi * frequency * t)
        return signal + baseline[np.newaxis, :]
    
    def generate_custom_ecg(self, params: Dict) -> np.ndarray:
        """Generate ECG with custom parameters."""
        abnormality = params.get("abnormality", "normal")
        heart_rate = params.get("heart_rate", 70.0)
        noise_level = params.get("noise_level", 0.0)
        baseline_wander = params.get("baseline_wander", False)
        duration = params.get("duration", self.duration)
        
        # Update duration if provided
        if duration != self.duration:
            self.duration = duration
            self.time_points = int(self.sampling_rate * duration)
        
        # Validate abnormality type
        valid_abnormalities = ["normal", "MI", "STTC", "CD", "HYP"]
        if abnormality not in valid_abnormalities:
            raise ValueError(f"Invalid abnormality: {abnormality}. Must be one of {valid_abnormalities}")
        
        generators = {
            "normal": self.generate_normal_ecg,
            "MI": self.generate_myocardial_infarction,
            "STTC": self.generate_sttc,
            "CD": self.generate_conduction_disturbance,
            "HYP": self.generate_hypertrophy
        }
        
        signal = generators[abnormality](heart_rate)
        
        if noise_level > 0:
            signal = self.add_noise(signal, noise_level)
        
        if baseline_wander:
            signal = self.add_baseline_wander(signal)
        
        return signal


# Global instance
ecg_simulator = ECGSimulator()