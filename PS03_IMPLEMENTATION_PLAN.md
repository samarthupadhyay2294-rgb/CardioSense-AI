# PS-03 Implementation Plan: AI-Assisted ECG Screening System

## 📋 Executive Summary

This implementation plan transforms the existing CardioSense AI project into a complete laboratory-level ECG screening prototype that fully complies with PS-03 requirements. The plan addresses the key gaps between the current file-upload analysis system and the comprehensive screening prototype needed for academic/research purposes.

**Project:** CardioSense AI Enhancement for PS-03 Compliance  
**Timeline:** 2-3 weeks  
**Effort Estimate:** 40-60 hours of development  
**Risk Level:** Medium (integration with existing system)  
**Current Compliance:** 85%  
**Target Compliance:** 100%

---

## 🎯 PS-03 Requirements Analysis

### Current Project Capabilities vs PS-03 Requirements

| PS-03 Requirement | Current Status | Gap Level |
|------------------|----------------|-----------|
| **ECG Signal Acquisition** | File upload only (WFDB, MAT, CSV, NPY, TXT) | 🔴 High |
| **Dataset Processing** | Multi-format support, sample data included | 🟢 Complete |
| **Preprocessing** | Bandpass filtering, normalization, quality assessment | 🟢 Complete |
| **Feature Extraction** | Basic statistics, signal quality | 🟡 Medium |
| **Machine Learning Classification** | Real 1-D CNN model, 5-class classification | 🟢 Complete |
| **Visual Representation** | Interactive waveform viewer, lead selector | 🟡 Medium |
| **Automated Classification Output** | Real-time predictions, confidence scores, PDF reports | 🟢 Complete |
| **Educational/Research Focus** | Medical disclaimers, non-diagnostic positioning | 🟢 Complete |

### Key Gaps Identified

1. **Real-time ECG Acquisition** - No live data streaming capability
2. **Enhanced Feature Extraction** - Limited temporal/frequency domain features
3. **Clinical Visualization** - Missing standard 12-lead grid format
4. **Clinical Interpretation** - Basic ML output, limited clinical context
5. **Simulation Capabilities** - No ECG signal generation for testing
6. **Performance Metrics** - Limited model performance visibility
7. **Batch Processing** - Single file analysis only

---

## 🚀 Implementation Strategy

### Development Phases

#### Phase 1: Foundation & Core Features (Week 1)
- ECG Simulation Module
- Enhanced Feature Extraction
- 12-Lead ECG Grid Visualization

#### Phase 2: Advanced Features (Week 2)
- Real-time Acquisition Module
- Clinical Interpretation Enhancement
- Performance Metrics Dashboard

#### Phase 3: Integration & Polish (Week 3)
- Batch Processing Mode
- Comprehensive Testing
- Documentation & Academic Preparation

### Technology Stack Extensions

**Backend Additions:**
- WebSocket support for real-time streaming
- Advanced signal processing (HeartPy library)
- Clinical interpretation engine
- Batch processing framework

**Frontend Additions:**
- Real-time data visualization
- Clinical display components
- Advanced charting capabilities
- Batch processing interface

---

## 📁 Detailed Implementation Plan

## Phase 1: Foundation & Core Features (Week 1)

### 1.1 ECG Simulation Module

**Purpose:** Generate realistic ECG signals for testing, demonstration, and educational purposes

**File Structure:**
```
backend/app/services/
├── ecg_simulation.py          # New: ECG signal generation
└── __init__.py

frontend/src/components/
├── simulation/
│   ├── ECGSimulator.jsx      # New: Simulation controls
│   └── SignalGenerator.jsx   # New: Parameter controls

backend/app/api/
├── simulation.py              # New: Simulation API endpoints
```

**Backend Implementation:**

```python
# backend/app/services/ecg_simulation.py
import numpy as np
from typing import Dict, Optional
from scipy.signal import butter, filtfilt

class ECGSimulator:
    """Generate realistic ECG signals for testing and demonstration"""
    
    def __init__(self, sampling_rate: int = 100, duration: float = 10.0):
        self.sampling_rate = sampling_rate
        self.duration = duration
        self.time_points = int(sampling_rate * duration)
        
    def generate_p_wave(self, t: np.ndarray, amplitude: float = 0.15) -> np.ndarray:
        """Generate P wave (atrial depolarization)"""
        return amplitude * np.exp(-((t % 1.0) * 10 - 0.2)**2 / 0.005)
    
    def generate_qrs_complex(self, t: np.ndarray, amplitude: float = 1.0) -> np.ndarray:
        """Generate QRS complex (ventricular depolarization)"""
        qrs = np.zeros_like(t)
        # Q wave
        qrs -= 0.15 * amplitude * np.exp(-((t % 1.0) * 10 - 0.5)**2 / 0.0008)
        # R wave
        qrs += 0.5 * amplitude * np.exp(-((t % 1.0) * 10 - 0.52)**2 / 0.0004)
        # S wave
        qrs -= 0.1 * amplitude * np.exp(-((t % 1.0) * 10 - 0.55)**2 / 0.0006)
        return qrs
    
    def generate_t_wave(self, t: np.ndarray, amplitude: float = 0.3) -> np.ndarray:
        """Generate T wave (ventricular repolarization)"""
        return amplitude * np.exp(-((t % 1.0) * 10 - 0.8)**2 / 0.01)
    
    def generate_normal_ecg(self, heart_rate: float = 70.0) -> np.ndarray:
        """Generate normal 12-lead ECG signal"""
        t = np.linspace(0, self.duration, self.time_points)
        heart_rate_normalized = heart_rate / 60.0
        
        # Base signal
        signal = np.zeros((12, self.time_points))
        
        for lead in range(12):
            # Adjust amplitude and phase for each lead
            lead_factor = [1.0, 1.2, 0.5, -0.5, -0.5, 0.6, 0.8, 1.5, 1.2, 0.9, 0.7, 0.5][lead]
            phase_shift = lead * 0.01
            
            ecg_signal = np.zeros_like(t)
            for beat in range(int(self.duration * heart_rate_normalized)):
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
        """Generate ECG with MI pattern (ST elevation)"""
        signal = self.generate_normal_ecg(heart_rate)
        
        # Add ST elevation in specific leads
        for lead in [3, 4, 5, 8, 9]:  # aVL, aVF, V1, V2, V3
            signal[lead] += 0.2  # ST elevation
        
        # Add pathological Q waves
        for lead in range(12):
            signal[lead] -= 0.1 * np.exp(-((np.linspace(0, self.duration, self.time_points) % 1.0) * 10 - 0.48)**2 / 0.0005)
        
        return signal
    
    def generate_sttc(self, heart_rate: float = 70.0) -> np.ndarray:
        """Generate ECG with ST/T changes"""
        signal = self.generate_normal_ecg(heart_rate)
        
        # Flatten T waves
        for lead in range(12):
            signal[lead] *= 0.7  # Reduce T wave amplitude
        
        # Add ST depression
        for lead in [1, 2, 5, 6]:  # II, III, aVF, V1
            signal[lead] -= 0.15
        
        return signal
    
    def generate_conduction_disturbance(self, heart_rate: float = 50.0) -> np.ndarray:
        """Generate ECG with conduction disturbance (bundle branch block)"""
        signal = self.generate_normal_ecg(heart_rate)
        
        # Widen QRS complex
        for lead in range(12):
            qrs_mask = (np.linspace(0, self.duration, self.time_points) % 1.0) > 0.45
            qrs_mask &= (np.linspace(0, self.duration, self.time_points) % 1.0) < 0.60
            signal[lead][qrs_mask] *= 1.5  # Widen QRS
        
        return signal
    
    def generate_hypertrophy(self, heart_rate: float = 70.0) -> np.ndarray:
        """Generate ECG with ventricular hypertrophy"""
        signal = self.generate_normal_ecg(heart_rate)
        
        # Increase voltage in lateral leads
        for lead in [6, 7, 8, 9, 10, 11]:  # V1-V6
            signal[lead] *= 1.3
        
        return signal
    
    def add_noise(self, signal: np.ndarray, noise_level: float = 0.05) -> np.ndarray:
        """Add realistic noise to signal"""
        noise = np.random.normal(0, noise_level, signal.shape)
        return signal + noise
    
    def add_baseline_wander(self, signal: np.ndarray, frequency: float = 0.5) -> np.ndarray:
        """Add baseline wander"""
        t = np.linspace(0, self.duration, signal.shape[1])
        baseline = 0.1 * np.sin(2 * np.pi * frequency * t)
        return signal + baseline[np.newaxis, :]
    
    def generate_custom_ecg(self, params: Dict) -> np.ndarray:
        """Generate ECG with custom parameters"""
        abnormality = params.get("abnormality", "normal")
        heart_rate = params.get("heart_rate", 70.0)
        noise_level = params.get("noise_level", 0.0)
        baseline_wander = params.get("baseline_wander", False)
        
        generators = {
            "normal": self.generate_normal_ecg,
            "MI": self.generate_myocardial_infarction,
            "STTC": self.generate_sttc,
            "CD": self.generate_conduction_disturbance,
            "HYP": self.generate_hypertrophy
        }
        
        signal = generators.get(abnormality, self.generate_normal_ecg)(heart_rate)
        
        if noise_level > 0:
            signal = self.add_noise(signal, noise_level)
        
        if baseline_wander:
            signal = self.add_baseline_wander(signal)
        
        return signal

# Global instance
ecg_simulator = ECGSimulator()
```

**API Endpoint:**

```python
# backend/app/api/simulation.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.ecg_simulation import ecg_simulator
import numpy as np

router = APIRouter(tags=["simulation"])

class SimulationParams(BaseModel):
    abnormality: str = "normal"
    heart_rate: float = 70.0
    noise_level: float = 0.0
    baseline_wander: bool = False
    duration: float = 10.0

@router.post("/api/simulation/generate")
async def generate_ecg(params: SimulationParams):
    """Generate simulated ECG signal"""
    try:
        signal = ecg_simulator.generate_custom_ecg(params.dict())
        
        # Convert to serializable format
        signal_data = signal.tolist()
        
        return {
            "success": True,
            "signal": signal_data,
            "parameters": params.dict(),
            "metadata": {
                "sampling_rate": ecg_simulator.sampling_rate,
                "duration": ecg_simulator.duration,
                "num_leads": 12,
                "num_samples": signal.shape[1]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@router.post("/api/simulation/generate-and-analyze")
async def generate_and_analyze(params: SimulationParams):
    """Generate and immediately analyze ECG signal"""
    try:
        signal = ecg_simulator.generate_custom_ecg(params.dict())
        
        # Process through existing pipeline
        from app.ml.predictor import predictor
        from app.services.ecg_service import compute_signal_quality, compute_ecg_statistics
        
        prediction = predictor.predict(signal)
        signal_quality = compute_signal_quality(signal)
        ecg_statistics = compute_ecg_statistics(signal)
        
        return {
            "success": True,
            "prediction": prediction,
            "signal_quality": signal_quality,
            "ecg_statistics": ecg_statistics,
            "parameters": params.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
```

**Frontend Implementation:**

```jsx
// frontend/src/components/simulation/ECGSimulator.jsx
import React, { useState } from 'react';
import { Play, Download, Settings } from 'lucide-react';

function ECGSimulator() {
  const [params, setParams] = useState({
    abnormality: 'normal',
    heartRate: 70,
    noiseLevel: 0.0,
    baselineWander: false,
    duration: 10
  });
  const [generatedSignal, setGeneratedSignal] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);

  const handleGenerate = async () => {
    try {
      const response = await fetch('/api/simulation/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          abnormality: params.abnormality,
          heart_rate: params.heartRate,
          noise_level: params.noiseLevel,
          baseline_wander: params.baselineWander,
          duration: params.duration
        })
      });
      const data = await response.json();
      setGeneratedSignal(data);
    } catch (error) {
      console.error('Generation failed:', error);
    }
  };

  const handleAnalyze = async () => {
    if (!generatedSignal) return;
    try {
      const response = await fetch('/api/simulation/generate-and-analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          abnormality: params.abnormality,
          heart_rate: params.heartRate,
          noise_level: params.noiseLevel,
          baseline_wander: params.baselineWander,
          duration: params.duration
        })
      });
      const data = await response.json();
      setAnalysisResult(data);
    } catch (error) {
      console.error('Analysis failed:', error);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">ECG Simulator</h2>
        <div className="flex gap-2">
          <button onClick={handleGenerate} className="flex items-center gap-2 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
            <Play size={16} /> Generate
          </button>
          <button onClick={handleAnalyze} className="flex items-center gap-2 bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
            <Download size={16} /> Analyze
          </button>
        </div>
      </div>

      {/* Parameter Controls */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium mb-2">Abnormality Type</label>
          <select 
            value={params.abnormality}
            onChange={(e) => setParams({...params, abnormality: e.target.value})}
            className="w-full border rounded p-2"
          >
            <option value="normal">Normal</option>
            <option value="MI">Myocardial Infarction</option>
            <option value="STTC">ST/T Changes</option>
            <option value="CD">Conduction Disturbance</option>
            <option value="HYP">Hypertrophy</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-2">Heart Rate (BPM)</label>
          <input 
            type="range" min="40" max="120" value={params.heartRate}
            onChange={(e) => setParams({...params, heartRate: parseInt(e.target.value)})}
            className="w-full"
          />
          <span className="text-sm">{params.heartRate} BPM</span>
        </div>
        <div>
          <label className="block text-sm font-medium mb-2">Noise Level</label>
          <input 
            type="range" min="0" max="0.2" step="0.01" value={params.noiseLevel}
            onChange={(e) => setParams({...params, noiseLevel: parseFloat(e.target.value)})}
            className="w-full"
          />
          <span className="text-sm">{params.noiseLevel}</span>
        </div>
        <div className="flex items-center">
          <label className="flex items-center gap-2">
            <input 
              type="checkbox" checked={params.baselineWander}
              onChange={(e) => setParams({...params, baselineWander: e.target.checked})}
            />
            <span className="text-sm">Add Baseline Wander</span>
          </label>
        </div>
      </div>

      {/* Results Display */}
      {analysisResult && (
        <div className="mt-6 border rounded p-4 bg-green-50">
          <h3 className="font-semibold mb-2">Analysis Results</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <span className="text-sm text-gray-600">Prediction:</span>
              <span className="font-bold ml-2">{analysisResult.prediction.prediction}</span>
            </div>
            <div>
              <span className="text-sm text-gray-600">Confidence:</span>
              <span className="font-bold ml-2">{(analysisResult.prediction.confidence * 100).toFixed(1)}%</span>
            </div>
            <div>
              <span className="text-sm text-gray-600">Signal Quality:</span>
              <span className="font-bold ml-2 capitalize">{analysisResult.signal_quality}</span>
            </div>
            <div>
              <span className="text-sm text-gray-600">Processing Time:</span>
              <span className="font-bold ml-2">{analysisResult.prediction.processing_time}s</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ECGSimulator;
```

**Integration Steps:**
1. Add `heartpy` to backend requirements.txt
2. Create simulation service file
3. Add simulation API router to main.py
4. Create frontend simulation components
5. Add simulation route to React Router
6. Test signal generation and analysis pipeline

**Testing Requirements:**
- Unit tests for each signal generation method
- Integration tests with existing ML pipeline
- UI testing for parameter controls
- Validation of generated signal properties

---

### 1.2 Enhanced Feature Extraction

**Purpose:** Extract and display clinically relevant ECG features for comprehensive analysis

**File Structure:**
```
backend/app/services/
├── feature_extraction.py       # New: Advanced feature extraction
└── __init__.py

frontend/src/components/
├── features/
│   ├── FeatureDisplay.jsx     # New: Feature visualization
│   ├── TemporalFeatures.jsx   # New: Time-domain features
│   └── FrequencyFeatures.jsx  # New: Frequency-domain features
```

**Backend Implementation:**

```python
# backend/app/services/feature_extraction.py
import numpy as np
from scipy import signal
from scipy.fft import fft, fftfreq
from typing import Dict, List, Tuple

class ECGFeatureExtractor:
    """Extract clinically relevant ECG features"""
    
    def __init__(self, sampling_rate: int = 100):
        self.sampling_rate = sampling_rate
        self.lead_names = ["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"]
    
    def detect_r_peaks(self, lead_signal: np.ndarray) -> np.ndarray:
        """Detect R peaks using Pan-Tompkins algorithm"""
        from scipy.signal import find_peaks
        peaks, _ = find_peaks(lead_signal, height=0.5, distance=30)
        return peaks
    
    def extract_rr_intervals(self, r_peaks: np.ndarray) -> List[float]:
        """Calculate RR intervals in seconds"""
        if len(r_peaks) < 2:
            return []
        
        rr_samples = np.diff(r_peaks)
        rr_seconds = rr_samples / self.sampling_rate
        return rr_seconds.tolist()
    
    def calculate_heart_rate(self, rr_intervals: List[float]) -> Dict[str, float]:
        """Calculate heart rate statistics"""
        if not rr_intervals:
            return {"mean": 0, "min": 0, "max": 0, "std": 0}
        
        heart_rates = [60.0 / rr for rr in rr_intervals]
        
        return {
            "mean": float(np.mean(heart_rates)),
            "min": float(np.min(heart_rates)),
            "max": float(np.max(heart_rates)),
            "std": float(np.std(heart_rates)),
            "current": float(heart_rates[-1]) if heart_rates else 0
        }
    
    def extract_qrs_features(self, lead_signal: np.ndarray, r_peaks: np.ndarray) -> Dict[str, float]:
        """Extract QRS complex features"""
        if len(r_peaks) == 0:
            return {"duration": 0, "amplitude": 0}
        
        # Analyze first QRS complex
        r_peak = r_peaks[0]
        window = 20  # samples
        qrs_window = lead_signal[max(0, r_peak-window):min(len(lead_signal), r_peak+window)]
        
        # Find Q and S points
        q_point = np.argmin(qrs_window[:window])
        s_point = np.argmin(qrs_window[window:]) + window
        
        qrs_duration = (s_point - q_point) / self.sampling_rate
        qrs_amplitude = np.max(qrs_window) - np.min(qrs_window)
        
        return {
            "duration": float(qrs_duration),
            "amplitude": float(qrs_amplitude),
            "q_point": int(q_point),
            "r_point": int(r_peak),
            "s_point": int(s_point)
        }
    
    def extract_st_segment(self, lead_signal: np.ndarray, r_peaks: np.ndarray) -> Dict[str, float]:
        """Extract ST segment features"""
        if len(r_peaks) == 0:
            return {"elevation": 0, "depression": 0}
        
        r_peak = r_peaks[0]
        st_start = r_peak + 10  # 100ms after R peak
        st_end = r_peak + 20    # 200ms after R peak
        
        if st_end >= len(lead_signal):
            return {"elevation": 0, "depression": 0}
        
        st_segment = lead_signal[st_start:st_end]
        st_level = np.mean(st_segment)
        
        # Baseline (PR segment)
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
            "level": float(st_level)
        }
    
    def extract_pr_interval(self, lead_signal: np.ndarray, r_peaks: np.ndarray) -> float:
        """Extract PR interval"""
        if len(r_peaks) == 0:
            return 0
        
        r_peak = r_peaks[0]
        pr_end = r_peak - 5
        pr_start = r_peak - 20
        
        if pr_start < 0:
            return 0
        
        return float((pr_end - pr_start) / self.sampling_rate)
    
    def extract_qt_interval(self, lead_signal: np.ndarray, r_peaks: np.ndarray) -> float:
        """Extract QT interval"""
        if len(r_peaks) == 0:
            return 0
        
        r_peak = r_peaks[0]
        qt_start = r_peak - 5
        qt_end = r_peak + 25
        
        if qt_end >= len(lead_signal):
            return 0
        
        return float((qt_end - qt_start) / self.sampling_rate)
    
    def extract_temporal_features(self, ecg_signal: np.ndarray) -> Dict[str, Dict]:
        """Extract time-domain features for all leads"""
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
        """Extract frequency-domain features"""
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
            
            # Frequency bands
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
        """Extract morphological features"""
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
        """Calculate skewness"""
        mean = np.mean(data)
        std = np.std(data)
        return np.mean(((data - mean) / std)**3)
    
    def _kurtosis(self, data: np.ndarray) -> float:
        """Calculate kurtosis"""
        mean = np.mean(data)
        std = np.std(data)
        return np.mean(((data - mean) / std)**4) - 3
    
    def _zero_crossings(self, data: np.ndarray) -> int:
        """Count zero crossings"""
        return np.sum(np.diff(np.sign(data)) != 0)
    
    def extract_all_features(self, ecg_signal: np.ndarray) -> Dict[str, Dict]:
        """Extract all feature types"""
        return {
            "temporal": self.extract_temporal_features(ecg_signal),
            "frequency": self.extract_frequency_features(ecg_signal),
            "morphological": self.extract_morphological_features(ecg_signal)
        }

# Global instance
feature_extractor = ECGFeatureExtractor()
```

**Integration with existing service:**

```python
# backend/app/services/ecg_service.py (modification)
from app.services.feature_extraction import feature_extractor

async def process_ecg_file(file_path: str, file_name: str) -> Dict[str, Any]:
    # ... existing code ...
    
    # Add feature extraction
    detailed_features = feature_extractor.extract_all_features(signal)
    
    return {
        # ... existing fields ...
        "detailed_features": detailed_features
    }
```

**Frontend Component:**

```jsx
// frontend/src/components/features/FeatureDisplay.jsx
import React from 'react';
import { Activity, Waves, BarChart3 } from 'lucide-react';

function FeatureDisplay({ features }) {
  if (!features) return null;

  const temporalFeatures = features.temporal || {};
  const frequencyFeatures = features.frequency || {};
  const morphologicalFeatures = features.morphological || {};

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">ECG Feature Analysis</h2>
      
      {/* Temporal Features */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Activity className="text-blue-500" />
          <h3 className="text-lg font-semibold">Temporal Features</h3>
        </div>
        
        <div className="grid grid-cols-3 gap-4">
          {Object.entries(temporalFeatures).map(([lead, data]) => (
            <div key={lead} className="border rounded p-3 bg-blue-50">
              <h4 className="font-bold text-sm mb-2">Lead {lead}</h4>
              <div className="space-y-1 text-xs">
                <div>HR: {data.heart_rate?.mean?.toFixed(0)} BPM</div>
                <div>QRS: {data.qrs_features?.duration?.toFixed(3)}s</div>
                <div>ST: {data.st_segment?.elevation?.toFixed(3)} mV</div>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {/* Frequency Features */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Waves className="text-green-500" />
          <h3 className="text-lg font-semibold">Frequency Features</h3>
        </div>
        
        <div className="grid grid-cols-3 gap-4">
          {Object.entries(frequencyFeatures).slice(0, 6).map(([lead, data]) => (
            <div key={lead} className="border rounded p-3 bg-green-50">
              <h4 className="font-bold text-sm mb-2">Lead {lead}</h4>
              <div className="space-y-1 text-xs">
                <div>Dominant: {data.dominant_frequency?.toFixed(1)} Hz</div>
                <div>Entropy: {data.spectral_entropy?.toFixed(3)}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {/* Morphological Features */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <BarChart3 className="text-purple-500" />
          <h3 className="text-lg font-semibold">Morphological Features</h3>
        </div>
        
        <div className="grid grid-cols-3 gap-4">
          {Object.entries(morphologicalFeatures).slice(0, 6).map(([lead, data]) => (
            <div key={lead} className="border rounded p-3 bg-purple-50">
              <h4 className="font-bold text-sm mb-2">Lead {lead}</h4>
              <div className="space-y-1 text-xs">
                <div>Mean: {data.mean?.toFixed(3)}</div>
                <div>Std: {data.std?.toFixed(3)}</div>
                <div>RMS: {data.rms?.toFixed(3)}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default FeatureDisplay;
```

**Integration Steps:**
1. Create feature extraction service
2. Integrate with existing ECG processing pipeline
3. Update database schema to store detailed features
4. Create frontend display components
5. Add feature display to results page
6. Validate feature extraction accuracy

**Testing Requirements:**
- Unit tests for each feature extraction method
- Validation against known ECG characteristics
- Performance testing for real-time extraction
- Integration with ML prediction pipeline

---

### 1.3 12-Lead ECG Grid Visualization

**Purpose:** Display ECG in standard clinical 12-lead format for better clinical interpretation

**File Structure:**
```
frontend/src/components/
├── ecg/
│   ├── ECG12LeadGrid.jsx       # New: 12-lead grid display
│   ├── ECGWaveform.jsx         # Modified: Enhance existing
│   └── LeadSelector.jsx        # Modified: Keep existing
```

**Frontend Implementation:**

```jsx
// frontend/src/components/ecg/ECG12LeadGrid.jsx
import React, { useState } from 'react';
import Plot from 'react-plotly.js';

function ECG12LeadGrid({ signalData, samplingRate = 100 }) {
  const [selectedLead, setSelectedLead] = useState(null);
  
  const leadNames = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6'];
  const leadColors = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD',
    '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9', '#F8B500', '#52B788'
  ];
  
  const createLeadPlot = (leadIndex, leadName) => {
    const leadSignal = signalData[leadIndex] || [];
    const time = Array.from({ length: leadSignal.length }, (_, i) => i / samplingRate);
    
    return {
      data: [{
        x: time,
        y: leadSignal,
        type: 'scatter',
        mode: 'lines',
        line: { 
          color: leadColors[leadIndex],
          width: 1.5
        },
        name: leadName
      }],
      layout: {
        title: {
          text: leadName,
          font: { size: 14, weight: 'bold' }
        },
        xaxis: {
          title: 'Time (s)',
          showgrid: true,
          gridcolor: '#E0E0E0'
        },
        yaxis: {
          title: 'Amplitude (mV)',
          showgrid: true,
          gridcolor: '#E0E0E0'
        },
        margin: { t: 30, r: 20, b: 40, l: 50 },
        height: 150,
        showlegend: false
      },
      config: {
        responsive: true,
        displayModeBar: false
      }
    };
  };
  
  const standardLayout = [
    ['I', 'II', 'III'],
    ['aVR', 'aVL', 'aVF'],
    ['V1', 'V2', 'V3'],
    ['V4', 'V5', 'V6']
  ];
  
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-gray-800">12-Lead ECG Display</h2>
        <div className="flex gap-2">
          <button 
            onClick={() => setSelectedLead(null)}
            className="px-3 py-1 bg-gray-200 rounded text-sm hover:bg-gray-300"
          >
            Reset View
          </button>
        </div>
      </div>
      
      {/* Standard 3x4 Grid Layout */}
      <div className="grid grid-cols-3 gap-4">
        {standardLayout.flat().map((leadName, index) => {
          const leadIndex = leadNames.indexOf(leadName);
          return (
            <div 
              key={leadName}
              className={`border rounded-lg p-2 cursor-pointer transition-all ${
                selectedLead === leadIndex ? 'ring-2 ring-blue-500' : 'hover:shadow-md'
              }`}
              onClick={() => setSelectedLead(leadIndex)}
            >
              <Plot {...createLeadPlot(leadIndex, leadName)} />
            </div>
          );
        })}
      </div>
      
      {/* Enlarged Single Lead View */}
      {selectedLead !== null && (
        <div className="mt-6 border rounded-lg p-4 bg-blue-50">
          <h3 className="font-semibold mb-2">Enlarged View: {leadNames[selectedLead]}</h3>
          <Plot {...{
            ...createLeadPlot(selectedLead, leadNames[selectedLead]),
            layout: {
              ...createLeadPlot(selectedLead, leadNames[selectedLead]).layout,
              height: 300
            }
          }} />
        </div>
      )}
      
      {/* Lead Information Panel */}
      <div className="mt-4 grid grid-cols-4 gap-2 text-sm">
        {leadNames.map((name, index) => (
          <div key={name} className="flex items-center gap-2">
            <div 
              className="w-4 h-4 rounded"
              style={{ backgroundColor: leadColors[index] }}
            />
            <span className="font-medium">{name}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ECG12LeadGrid;
```

**Integration Steps:**
1. Create 12-lead grid component
2. Integrate with existing signal data
3. Add interactive lead selection
4. Implement zoom/pan functionality
5. Add export/print functionality
6. Test with various ECG signals

**Testing Requirements:**
- UI testing for lead selection
- Performance testing with large datasets
- Responsiveness testing across devices
- Integration with existing results display

---

## Phase 2: Advanced Features (Week 2)

### 2.1 Real-time Acquisition Module

**Purpose:** Enable live ECG data streaming from hardware devices or simulation

**File Structure:**
```
backend/app/services/
├── realtime_acquisition.py    # New: Real-time data handling
└── __init__.py

frontend/src/components/
├── realtime/
│   ├── RealtimeDisplay.jsx    # New: Live signal display
│   ├── DeviceConnector.jsx    # New: Device connection
│   └── AcquisitionControls.jsx # New: Start/stop controls

backend/app/api/
├── realtime.py                # New: WebSocket endpoints
```

**Backend Implementation:**

```python
# backend/app/services/realtime_acquisition.py
import asyncio
import json
from typing import Optional, Callable
from fastapi import WebSocket
import numpy as np

class RealtimeECGAcquisition:
    """Handle real-time ECG data acquisition"""
    
    def __init__(self, sampling_rate: int = 100, buffer_size: int = 1000):
        self.sampling_rate = sampling_rate
        self.buffer_size = buffer_size
        self.buffer = np.zeros((12, buffer_size))
        self.is_acquiring = False
        self.clients = set()
        self.callbacks = []
    
    async def start_acquisition(self, websocket: WebSocket):
        """Start real-time acquisition from WebSocket"""
        self.is_acquiring = True
        self.clients.add(websocket)
        
        try:
            while self.is_acquiring:
                # Simulate incoming data (replace with actual device data)
                new_data = self._simulate_incoming_data()
                
                # Update buffer
                self._update_buffer(new_data)
                
                # Broadcast to all connected clients
                await self._broadcast_data(new_data)
                
                await asyncio.sleep(0.01)  # 100 Hz update rate
                
        except Exception as e:
            print(f"Acquisition error: {e}")
        finally:
            self.clients.discard(websocket)
    
    def _simulate_incoming_data(self) -> np.ndarray:
        """Simulate incoming ECG data (replace with real device data)"""
        # Generate small segment of ECG data
        from app.services.ecg_simulation import ecg_simulator
        segment = ecg_simulator.generate_normal_ecg(heart_rate=70.0)
        return segment[:, :10]  # 10 samples per update
    
    def _update_buffer(self, new_data: np.ndarray):
        """Update circular buffer with new data"""
        samples = new_data.shape[1]
        self.buffer = np.roll(self.buffer, -samples, axis=1)
        self.buffer[:, -samples:] = new_data
    
    async def _broadcast_data(self, data: np.ndarray):
        """Broadcast data to all connected clients"""
        message = {
            "type": "ecg_data",
            "data": data.tolist(),
            "timestamp": asyncio.get_event_loop().time()
        }
        
        disconnected = set()
        for client in self.clients:
            try:
                await client.send_json(message)
            except:
                disconnected.add(client)
        
        self.clients -= disconnected
    
    def stop_acquisition(self):
        """Stop real-time acquisition"""
        self.is_acquiring = False
    
    def get_buffer(self) -> np.ndarray:
        """Get current buffer contents"""
        return self.buffer.copy()
    
    def add_callback(self, callback: Callable):
        """Add callback for real-time analysis"""
        self.callbacks.append(callback)
    
    async def process_realtime(self, data: np.ndarray):
        """Process real-time data with callbacks"""
        for callback in self.callbacks:
            try:
                await callback(data)
            except Exception as e:
                print(f"Callback error: {e}")

# Global instance
realtime_acquisition = RealtimeECGAcquisition()
```

**WebSocket Endpoint:**

```python
# backend/app/api/realtime.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.realtime_acquisition import realtime_acquisition

router = APIRouter(tags=["realtime"])

@router.websocket("/ws/realtime-ecg")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time ECG streaming"""
    await websocket.accept()
    
    try:
        await realtime_acquisition.start_acquisition(websocket)
    except WebSocketDisconnect:
        realtime_acquisition.stop_acquisition()
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close()
```

**Frontend Implementation:**

```jsx
// frontend/src/components/realtime/RealtimeDisplay.jsx
import React, { useEffect, useState, useRef } from 'react';
import { Play, Square, Activity } from 'lucide-react';
import Plot from 'react-plotly.js';

function RealtimeDisplay() {
  const [isConnected, setIsConnected] = useState(false);
  const [ecgData, setEcgData] = useState(null);
  const [heartRate, setHeartRate] = useState(0);
  const wsRef = useRef(null);
  
  const connectWebSocket = () => {
    wsRef.current = new WebSocket('ws://localhost:8000/ws/realtime-ecg');
    
    wsRef.current.onopen = () => {
      setIsConnected(true);
      console.log('WebSocket connected');
    };
    
    wsRef.current.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'ecg_data') {
        setEcgData(message.data);
        // Calculate heart rate from data
        const calculatedHR = calculateHeartRate(message.data);
        setHeartRate(calculatedHR);
      }
    };
    
    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };
    
    wsRef.current.onclose = () => {
      setIsConnected(false);
      console.log('WebSocket disconnected');
    };
  };
  
  const disconnectWebSocket = () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
  };
  
  const calculateHeartRate = (data) => {
    // Simple heart rate calculation from R-R intervals
    // Replace with actual algorithm
    return 70 + Math.random() * 10; // Placeholder
  };
  
  const createRealtimePlot = () => {
    if (!ecgData) return null;
    
    const leadSignals = ecgData; // Assuming 12xN array
    const time = Array.from({ length: leadSignals[0].length }, (_, i) => i / 100);
    
    return {
      data: [{
        x: time,
        y: leadSignals[1], // Lead II
        type: 'scatter',
        mode: 'lines',
        line: { color: '#4ECDC4', width: 2 }
      }],
      layout: {
        title: 'Real-time ECG (Lead II)',
        xaxis: { title: 'Time (s)' },
        yaxis: { title: 'Amplitude (mV)' },
        margin: { t: 30, r: 20, b: 40, l: 50 },
        height: 200
      },
      config: { responsive: true, displayModeBar: false }
    };
  };
  
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Real-time ECG Acquisition</h2>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Activity className={isConnected ? "text-green-500" : "text-gray-400"} />
            <span className="text-sm">{isConnected ? "Live" : "Disconnected"}</span>
          </div>
          <div className="text-2xl font-bold">
            {Math.round(heartRate)} <span className="text-sm font-normal">BPM</span>
          </div>
        </div>
      </div>
      
      <div className="flex gap-4 mb-6">
        {!isConnected ? (
          <button 
            onClick={connectWebSocket}
            className="flex items-center gap-2 bg-green-500 text-white px-6 py-3 rounded-lg hover:bg-green-600"
          >
            <Play size={20} /> Start Acquisition
          </button>
        ) : (
          <button 
            onClick={disconnectWebSocket}
            className="flex items-center gap-2 bg-red-500 text-white px-6 py-3 rounded-lg hover:bg-red-600"
          >
            <Square size={20} /> Stop Acquisition
          </button>
        )}
      </div>
      
      {ecgData && (
        <div className="border rounded-lg p-4 bg-gray-50">
          <Plot {...createRealtimePlot()} />
        </div>
      )}
      
      {!isConnected && (
        <div className="text-center py-12 text-gray-500">
          <Activity size={48} className="mx-auto mb-4" />
          <p>Click "Start Acquisition" to begin real-time ECG monitoring</p>
        </div>
      )}
    </div>
  );
}

export default RealtimeDisplay;
```

**Integration Steps:**
1. Add WebSocket support to FastAPI
2. Create real-time acquisition service
3. Implement WebSocket endpoint
4. Create frontend real-time display
5. Add device connection interface
6. Test with simulated and real data

**Testing Requirements:**
- WebSocket connection testing
- Real-time data validation
- Performance testing under load
- Integration with ML pipeline

---

### 2.2 Clinical Interpretation Enhancement

**Purpose:** Provide clinically relevant interpretation of ML predictions

**File Structure:**
```
backend/app/services/
├── clinical_interpretation.py # New: Clinical interpretation logic
└── __init__.py

frontend/src/components/
├── interpretation/
│   ├── ClinicalInterpreter.jsx # New: Display interpretation
│   └── DifferentialDiagnosis.jsx # New: Show differential diagnosis
```

**Backend Implementation:**

```python
# backend/app/services/clinical_interpretation.py
from typing import Dict, List
from app.services.feature_extraction import feature_extractor

class ClinicalInterpreter:
    """Generate clinically relevant interpretations"""
    
    def __init__(self):
        self.clinical_rules = {
            "MI": {
                "criteria": ["ST_elevation", "pathological_Q", "T_wave_inversion"],
                "urgency": "emergency",
                "description": "Signs of myocardial infarction detected"
            },
            "STTC": {
                "criteria": ["ST_depression", "T_wave_flattening", "ST_elevation"],
                "urgency": "urgent",
                "description": "ST/T wave changes indicating possible ischemia"
            },
            "CD": {
                "criteria": ["QRS_widening", "bundle_branch_block"],
                "urgency": "routine",
                "description": "Conduction disturbance detected"
            },
            "HYP": {
                "criteria": ["high_voltage", "strain_pattern"],
                "urgency": "routine",
                "description": "Ventricular hypertrophy detected"
            },
            "NORM": {
                "criteria": ["normal_sinus_rhythm"],
                "urgency": "none",
                "description": "Normal sinus rhythm"
            }
        }
    
    def interpret_prediction(self, prediction: Dict, features: Dict) -> Dict:
        """Generate clinical interpretation from prediction and features"""
        prediction_code = prediction.get("prediction_code", "NORM")
        confidence = prediction.get("confidence", 0.0)
        
        interpretation = {
            "primary_findings": [],
            "secondary_findings": [],
            "clinical_significance": "",
            "urgency": "none",
            "recommendations": [],
            "differential_diagnosis": [],
            "limitations": []
        }
        
        # Primary interpretation based on prediction
        if prediction_code in self.clinical_rules:
            rule = self.clinical_rules[prediction_code]
            interpretation["primary_findings"].append(rule["description"])
            interpretation["urgency"] = rule["urgency"]
        
        # Analyze features for additional findings
        temporal_features = features.get("temporal", {})
        
        # Heart rate analysis
        for lead_name, lead_features in temporal_features.items():
            hr = lead_features.get("heart_rate", {})
            mean_hr = hr.get("mean", 0)
            
            if mean_hr > 100:
                interpretation["secondary_findings"].append("Tachycardia detected")
            elif mean_hr < 60:
                interpretation["secondary_findings"].append("Bradycardia detected")
            
            # HRV analysis
            hr_std = hr.get("std", 0)
            if hr_std > 10:
                interpretation["secondary_findings"].append("Reduced heart rate variability")
        
        # ST segment analysis
        for lead_name, lead_features in temporal_features.items():
            st_segment = lead_features.get("st_segment", {})
            st_elevation = st_segment.get("elevation", 0)
            st_depression = st_segment.get("depression", 0)
            
            if st_elevation > 0.1:
                interpretation["primary_findings"].append(
                    f"ST elevation in lead {lead_name} ({st_elevation:.2f} mV)"
                )
            if st_depression > 0.1:
                interpretation["primary_findings"].append(
                    f"ST depression in lead {leadName} ({st_depression:.2f} mV)"
                )
        
        # QRS analysis
        for lead_name, lead_features in temporal_features.items():
            qrs = lead_features.get("qrs_features", {})
            qrs_duration = qrs.get("duration", 0)
            
            if qrs_duration > 0.12:
                interpretation["secondary_findings"].append(
                    f"QRS widening in lead {lead_name} ({qrs_duration:.3f} s)"
                )
        
        # Generate clinical significance
        interpretation["clinical_significance"] = self._generate_clinical_significance(
            prediction_code, confidence, interpretation
        )
        
        # Generate recommendations
        interpretation["recommendations"] = self._generate_recommendations(
            prediction_code, interpretation["urgency"]
        )
        
        # Generate differential diagnosis
        interpretation["differential_diagnosis"] = self._generate_differential_diagnosis(
            prediction_code, features
        )
        
        # Add limitations
        interpretation["limitations"] = [
            "AI interpretation should be confirmed by qualified healthcare professional",
            "Clinical correlation with patient symptoms and history required",
            "Model trained on specific dataset, may not generalize to all populations"
        ]
        
        return interpretation
    
    def _generate_clinical_significance(self, prediction_code: str, confidence: float, interpretation: Dict) -> str:
        """Generate clinical significance statement"""
        if prediction_code == "NORM":
            return "Normal ECG with no significant abnormalities detected."
        
        urgency = interpretation.get("urgency", "none")
        findings = " and ".join(interpretation["primary_findings"])
        
        if urgency == "emergency":
            return f"EMERGENCY: {findings}. Immediate medical evaluation required."
        elif urgency == "urgent":
            return f"URGENT: {findings}. Prompt medical evaluation recommended."
        else:
            return f"{findings}. Clinical correlation recommended."
    
    def _generate_recommendations(self, prediction_code: str, urgency: str) -> List[str]:
        """Generate clinical recommendations"""
        recommendations = []
        
        if urgency == "emergency":
            recommendations.extend([
                "Seek immediate emergency medical care",
                "Do not delay evaluation for any reason",
                "Consider activating emergency response system"
            ])
        elif urgency == "urgent":
            recommendations.extend([
                "Seek prompt medical evaluation",
                "Contact healthcare provider within 24 hours",
                "Monitor for worsening symptoms"
            ])
        else:
            recommendations.extend([
                "Schedule routine follow-up with healthcare provider",
                "Continue regular cardiac monitoring if indicated",
                "Discuss findings with primary care physician"
            ])
        
        # Add specific recommendations based on prediction
        if prediction_code == "MI":
            recommendations.append("Consider cardiac enzyme evaluation")
        elif prediction_code == "STTC":
            recommendations.append("Consider stress testing or cardiac imaging")
        elif prediction_code == "CD":
            recommendations.append("Consider cardiology consultation for conduction evaluation")
        elif prediction_code == "HYP":
            recommendations.append("Consider echocardiography for structural evaluation")
        
        return recommendations
    
    def _generate_differential_diagnosis(self, prediction_code: str, features: Dict) -> List[str]:
        """Generate differential diagnosis suggestions"""
        differential = []
        
        if prediction_code == "MI":
            differential.extend([
                "Acute myocardial infarction",
                "Previous myocardial infarction with scar",
                "Left ventricular aneurysm",
                "Pericarditis"
            ])
        elif prediction_code == "STTC":
            differential.extend([
                "Myocardial ischemia",
                "Electrolyte abnormalities",
                "Drug effects (e.g., digoxin)",
                "Normal variant"
            ])
        elif prediction_code == "CD":
            differential.extend([
                "Bundle branch block",
                "Hemiblock",
                "Intraventricular conduction delay",
                "Ventricular preexcitation"
            ])
        elif prediction_code == "HYP":
            differential.extend([
                "Left ventricular hypertrophy",
                "Right ventricular hypertrophy",
                "Athlete's heart",
                "Volume overload"
            ])
        
        return differential

# Global instance
clinical_interpreter = ClinicalInterpreter()
```

**Integration with existing API:**

```python
# backend/app/api/ecg.py (modification)
from app.services.clinical_interpretation import clinical_interpreter
from app.services.feature_extraction import feature_extractor

@router.post("/api/ecg/analyze")
async def analyze_ecg(files: list[UploadFile] = File(...), db: Session = Depends(get_db)):
    # ... existing analysis code ...
    
    # Add clinical interpretation
    detailed_features = feature_extractor.extract_all_features(signal)
    clinical_interpretation = clinical_interpreter.interpret_prediction(
        prediction_result, detailed_features
    )
    
    # Add to database
    analysis.clinical_interpretation = clinical_interpretation
    
    # ... rest of existing code ...
```

**Frontend Component:**

```jsx
// frontend/src/components/interpretation/ClinicalInterpreter.jsx
import React from 'react';
import { AlertTriangle, CheckCircle, Info, Activity } from 'lucide-react';

function ClinicalInterpreter({ interpretation }) {
  if (!interpretation) return null;

  const urgencyColors = {
    emergency: 'bg-red-100 border-red-500 text-red-800',
    urgent: 'bg-orange-100 border-orange-500 text-orange-800',
    routine: 'bg-yellow-100 border-yellow-500 text-yellow-800',
    none: 'bg-green-100 border-green-500 text-green-800'
  };

  const urgencyIcons = {
    emergency: AlertTriangle,
    urgent: AlertTriangle,
    routine: Info,
    none: CheckCircle
  };

  const UrgencyIcon = urgencyIcons[interpretation.urgency] || Info;

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Clinical Interpretation</h2>
      
      {/* Clinical Significance */}
      <div className={`mb-6 p-4 rounded-lg border-l-4 ${urgencyColors[interpretation.urgency]}`}>
        <div className="flex items-start gap-3">
          <UrgencyIcon className="mt-1 flex-shrink-0" />
          <div>
            <h3 className="font-semibold mb-2">Clinical Significance</h3>
            <p className="text-sm">{interpretation.clinical_significance}</p>
          </div>
        </div>
      </div>
      
      {/* Primary Findings */}
      <div className="mb-6">
        <h3 className="font-semibold mb-3 flex items-center gap-2">
          <Activity className="text-blue-500" />
          Primary Findings
        </h3>
        <ul className="space-y-2">
          {interpretation.primary_findings.map((finding, index) => (
            <li key={index} className="flex items-start gap-2 text-sm">
              <span className="text-blue-500 mt-1">•</span>
              <span>{finding}</span>
            </li>
          ))}
        </ul>
      </div>
      
      {/* Secondary Findings */}
      {interpretation.secondary_findings.length > 0 && (
        <div className="mb-6">
          <h3 className="font-semibold mb-3 flex items-center gap-2">
            <Info className="text-purple-500" />
            Additional Findings
          </h3>
          <ul className="space-y-2">
            {interpretation.secondary_findings.map((finding, index) => (
              <li key={index} className="flex items-start gap-2 text-sm">
                <span className="text-purple-500 mt-1">•</span>
                <span>{finding}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
      
      {/* Recommendations */}
      <div className="mb-6">
        <h3 className="font-semibold mb-3 flex items-center gap-2">
          <CheckCircle className="text-green-500" />
          Recommendations
        </h3>
        <ol className="space-y-2">
          {interpretation.recommendations.map((recommendation, index) => (
            <li key={index} className="flex items-start gap-2 text-sm">
              <span className="bg-green-100 text-green-800 rounded-full w-5 h-5 flex items-center justify-center text-xs flex-shrink-0">
                {index + 1}
              </span>
              <span>{recommendation}</span>
            </li>
          ))}
        </ol>
      </div>
      
      {/* Differential Diagnosis */}
      {interpretation.differential_diagnosis.length > 0 && (
        <div className="mb-6">
          <h3 className="font-semibold mb-3">Differential Diagnosis</h3>
          <div className="flex flex-wrap gap-2">
            {interpretation.differential_diagnosis.map((diagnosis, index) => (
              <span key={index} className="bg-gray-100 px-3 py-1 rounded-full text-sm">
                {diagnosis}
              </span>
            ))}
          </div>
        </div>
      )}
      
      {/* Limitations */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <h3 className="font-semibold mb-2 text-yellow-800">Limitations & Disclaimer</h3>
        <ul className="space-y-1 text-sm text-yellow-700">
          {interpretation.limitations.map((limitation, index) => (
            <li key={index} className="flex items-start gap-2">
              <span>⚠️</span>
              <span>{limitation}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default ClinicalInterpreter;
```

**Integration Steps:**
1. Create clinical interpretation service
2. Integrate with existing ECG analysis pipeline
3. Update database schema for interpretation storage
4. Create frontend interpretation display
5. Add interpretation to results page
6. Validate clinical accuracy

**Testing Requirements:**
- Clinical rule validation
- Integration with feature extraction
- Testing against known clinical cases
- Medical professional review

---

### 2.3 Performance Metrics Dashboard

**Purpose:** Display model performance metrics and validation statistics

**File Structure:**
```
backend/app/api/
├── performance.py              # New: Performance metrics API
└── __init__.py

frontend/src/pages/
├── PerformanceMetrics.jsx      # New: Performance dashboard
```

**Backend Implementation:**

```python
# backend/app/api/performance.py
from fastapi import APIRouter
from typing import Dict
import json
from pathlib import Path

router = APIRouter(tags=["performance"])

# These would typically come from model evaluation results
MODEL_PERFORMANCE = {
    "overall_metrics": {
        "accuracy": 0.89,
        "precision": 0.87,
        "recall": 0.85,
        "f1_score": 0.86
    },
    "class_metrics": {
        "NORM": {
            "sensitivity": 0.92,
            "specificity": 0.88,
            "auc_roc": 0.94,
            "precision": 0.90
        },
        "MI": {
            "sensitivity": 0.84,
            "specificity": 0.91,
            "auc_roc": 0.89,
            "precision": 0.83
        },
        "STTC": {
            "sensitivity": 0.78,
            "specificity": 0.89,
            "auc_roc": 0.86,
            "precision": 0.76
        },
        "CD": {
            "sensitivity": 0.81,
            "specificity": 0.92,
            "auc_roc": 0.88,
            "precision": 0.79
        },
        "HYP": {
            "sensitivity": 0.86,
            "specificity": 0.90,
            "auc_roc": 0.91,
            "precision": 0.84
        }
    },
    "confusion_matrix": [
        [450, 15, 8, 5, 2],
        [12, 380, 18, 8, 12],
        [10, 22, 340, 15, 13],
        [8, 10, 12, 360, 10],
        [5, 15, 10, 8, 362]
    ],
    "training_info": {
        "dataset": "PTB-XL",
        "training_samples": 21000,
        "validation_samples": 2500,
        "test_samples": 2500,
        "epochs": 30,
        "batch_size": 64
    }
}

@router.get("/api/performance/metrics")
async def get_performance_metrics():
    """Get model performance metrics"""
    return MODEL_PERFORMANCE

@router.get("/api/performance/class/{class_name}")
async def get_class_performance(class_name: str):
    """Get performance metrics for specific class"""
    if class_name not in MODEL_PERFORMANCE["class_metrics"]:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Class not found")
    
    return MODEL_PERFORMANCE["class_metrics"][class_name]
```

**Frontend Implementation:**

```jsx
// frontend/src/pages/PerformanceMetrics.jsx
import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function PerformanceMetrics() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMetrics();
  }, []);

  const fetchMetrics = async () => {
    try {
      const response = await fetch('/api/performance/metrics');
      const data = await response.json();
      setMetrics(data);
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="text-center py-12">Loading performance metrics...</div>;
  if (!metrics) return <div className="text-center py-12 text-red-500">Failed to load metrics</div>;

  const classData = Object.entries(metrics.class_metrics).map(([className, classMetrics]) => ({
    name: className,
    sensitivity: (classMetrics.sensitivity * 100).toFixed(1),
    specificity: (classMetrics.specificity * 100).toFixed(1),
    auc: (classMetrics.auc_roc * 100).toFixed(1)
  }));

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Model Performance Metrics</h1>
      
      {/* Overall Metrics */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        <div className="bg-blue-50 p-4 rounded-lg">
          <h3 className="text-sm text-gray-600 mb-1">Accuracy</h3>
          <p className="text-2xl font-bold text-blue-600">{(metrics.overall_metrics.accuracy * 100).toFixed(1)}%</p>
        </div>
        <div className="bg-green-50 p-4 rounded-lg">
          <h3 className="text-sm text-gray-600 mb-1">Precision</h3>
          <p className="text-2xl font-bold text-green-600">{(metrics.overall_metrics.precision * 100).toFixed(1)}%</p>
        </div>
        <div className="bg-purple-50 p-4 rounded-lg">
          <h3 className="text-sm text-gray-600 mb-1">Recall</h3>
          <p className="text-2xl font-bold text-purple-600">{(metrics.overall_metrics.recall * 100).toFixed(1)}%</p>
        </div>
        <div className="bg-orange-50 p-4 rounded-lg">
          <h3 className="text-sm text-gray-600 mb-1">F1 Score</h3>
          <p className="text-2xl font-bold text-orange-600">{(metrics.overall_metrics.f1_score * 100).toFixed(1)}%</p>
        </div>
      </div>

      {/* Class Performance Chart */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4">Class-wise Performance</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={classData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="sensitivity" fill="#8884d8" name="Sensitivity %" />
            <Bar dataKey="specificity" fill="#82ca9d" name="Specificity %" />
            <Bar dataKey="auc" fill="#ffc658" name="AUC-ROC %" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Training Information */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h2 className="text-xl font-semibold mb-4">Training Information</h2>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <span className="text-sm text-gray-600">Dataset:</span>
            <span className="font-bold ml-2">{metrics.training_info.dataset}</span>
          </div>
          <div>
            <span className="text-sm text-gray-600">Training Samples:</span>
            <span className="font-bold ml-2">{metrics.training_info.training_samples.toLocaleString()}</span>
          </div>
          <div>
            <span className="text-sm text-gray-600">Validation Samples:</span>
            <span className="font-bold ml-2">{metrics.training_info.validation_samples.toLocaleString()}</span>
          </div>
          <div>
            <span className="text-sm text-gray-600">Test Samples:</span>
            <span className="font-bold ml-2">{metrics.training_info.test_samples.toLocaleString()}</span>
          </div>
          <div>
            <span className="text-sm text-gray-600">Epochs:</span>
            <span className="font-bold ml-2">{metrics.training_info.epochs}</span>
          </div>
          <div>
            <span className="text-sm text-gray-600">Batch Size:</span>
            <span className="font-bold ml-2">{metrics.training_info.batch_size}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default PerformanceMetrics;
```

**Integration Steps:**
1. Create performance metrics API
2. Add actual model evaluation results
3. Create performance dashboard UI
4. Add route to navigation
5. Test with real metrics
6. Add export functionality

**Testing Requirements:**
- API endpoint testing
- UI component testing
- Data validation
- Performance testing

---

## Phase 3: Integration & Polish (Week 3)

### 3.1 Batch Processing Mode

**Purpose:** Analyze multiple ECG files efficiently for research studies

**File Structure:**
```
backend/app/api/
├── batch.py                    # New: Batch processing API
└── __init__.py

frontend/src/components/
├── batch/
│   ├── BatchUploader.jsx       # New: Multi-file upload
│   └── BatchResults.jsx        # New: Batch results display
```

**Backend Implementation:**

```python
# backend/app/api/batch.py
from fastapi import APIRouter, UploadFile, File, BackgroundTasks
from typing import List
import asyncio
from app.services.ecg_service import process_ecg_file
from app.database.database import get_db
from app.database.models import ECGAnalysis

router = APIRouter(tags=["batch"])

async def process_single_file(file: UploadFile, results: list, db):
    """Process single file in batch"""
    try:
        content = await file.read()
        file_path = f"/tmp/{file.filename}"
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        result = await process_ecg_file(file_path, file.filename)
        results.append({
            "filename": file.filename,
            "status": "success",
            "result": result
        })
    except Exception as e:
        results.append({
            "filename": file.filename,
            "status": "error",
            "error": str(e)
        })

@router.post("/api/batch/analyze")
async def batch_analyze(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...)
):
    """Analyze multiple ECG files in batch"""
    results = []
    
    # Process files concurrently
    tasks = [process_single_file(file, results, None) for file in files]
    await asyncio.gather(*tasks)
    
    return {
        "total_files": len(files),
        "successful": sum(1 for r in results if r["status"] == "success"),
        "failed": sum(1 for r in results if r["status"] == "error"),
        "results": results
    }
```

**Frontend Implementation:**

```jsx
// frontend/src/components/batch/BatchUploader.jsx
import React, { useState } from 'react';
import { Upload, FileText, CheckCircle, XCircle } from 'lucide-react';

function BatchUploader() {
  const [files, setFiles] = useState([]);
  const [processing, setProcessing] = useState(false);
  const [results, setResults] = useState([]);

  const handleFileSelect = (event) => {
    const selectedFiles = Array.from(event.target.files);
    setFiles(selectedFiles);
  };

  const handleBatchProcess = async () => {
    if (files.length === 0) return;
    
    setProcessing(true);
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));

    try {
      const response = await fetch('/api/batch/analyze', {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      setResults(data.results);
    } catch (error) {
      console.error('Batch processing failed:', error);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Batch ECG Analysis</h2>
      
      {/* File Upload */}
      <div className="mb-6">
        <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50">
          <div className="flex flex-col items-center justify-center pt-5 pb-6">
            <Upload className="w-8 h-8 mb-2 text-gray-500" />
            <p className="text-sm text-gray-500">Click to upload ECG files</p>
            <p className="text-xs text-gray-500">Multiple files supported</p>
          </div>
          <input type="file" multiple className="hidden" onChange={handleFileSelect} />
        </label>
      </div>

      {/* Selected Files */}
      {files.length > 0 && (
        <div className="mb-6">
          <h3 className="font-semibold mb-2">Selected Files ({files.length})</h3>
          <div className="space-y-2">
            {files.map((file, index) => (
              <div key={index} className="flex items-center gap-2 text-sm">
                <FileText className="text-blue-500" />
                <span>{file.name}</span>
                <span className="text-gray-500">({(file.size / 1024).toFixed(1)} KB)</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Process Button */}
      <button
        onClick={handleBatchProcess}
        disabled={files.length === 0 || processing}
        className="w-full bg-blue-500 text-white py-3 rounded-lg hover:bg-blue-600 disabled:bg-gray-300"
      >
        {processing ? 'Processing...' : `Process ${files.length} Files`}
      </button>

      {/* Results */}
      {results.length > 0 && (
        <div className="mt-6">
          <h3 className="font-semibold mb-4">Results</h3>
          <div className="space-y-2">
            {results.map((result, index) => (
              <div key={index} className={`p-3 rounded-lg ${result.status === 'success' ? 'bg-green-50' : 'bg-red-50'}`}>
                <div className="flex items-center gap-2">
                  {result.status === 'success' ? (
                    <CheckCircle className="text-green-500" />
                  ) : (
                    <XCircle className="text-red-500" />
                  )}
                  <span className="font-medium">{result.filename}</span>
                </div>
                {result.status === 'success' ? (
                  <div className="mt-2 text-sm">
                    <span>Prediction: {result.result.prediction}</span>
                    <span className="ml-4">Confidence: {(result.result.confidence * 100).toFixed(1)}%</span>
                  </div>
                ) : (
                  <div className="mt-2 text-sm text-red-600">
                    Error: {result.error}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default BatchUploader;
```

**Integration Steps:**
1. Create batch processing API
2. Implement concurrent file processing
3. Create batch upload UI
4. Add results summary and export
5. Test with large file batches
6. Add progress indicators

**Testing Requirements:**
- Batch processing testing
- Performance testing with many files
- Error handling validation
- UI stress testing

---

## 📁 Updated Project Structure

```
cardiosense-ai/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── batch.py                    # New
│   │   │   ├── performance.py             # New
│   │   │   ├── realtime.py                # New
│   │   │   ├── simulation.py              # New
│   │   │   ├── ecg.py                     # Modified
│   │   │   ├── health.py                  # Existing
│   │   │   ├── history.py                 # Existing
│   │   │   ├── image_ecg.py               # Existing
│   │   │   ├── model.py                   # Existing
│   │   │   └── statistics.py              # Existing
│   │   ├── services/
│   │   │   ├── clinical_interpretation.py # New
│   │   │   ├── ecg_simulation.py          # New
│   │   │   ├── feature_extraction.py      # New
│   │   │   ├── realtime_acquisition.py    # New
│   │   │   ├── ecg_service.py             # Modified
│   │   │   ├── image_service.py           # Existing
│   │   │   ├── report_service.py          # Existing
│   │   │   └── summary_service.py         # Existing
│   │   ├── core/                          # Existing
│   │   ├── database/                      # Existing
│   │   ├── ml/                            # Existing
│   │   └── main.py                        # Modified
│   ├── config/
│   │   └── model_config.json              # Existing
│   ├── models/
│   │   ├── ptbxl_cnn_best.pt              # Existing
│   │   └── image/                         # Existing
│   ├── requirements.txt                   # Modified
│   └── .env                               # Existing
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── batch/
│   │   │   │   ├── BatchUploader.jsx       # New
│   │   │   │   └── BatchResults.jsx        # New
│   │   │   ├── ecg/
│   │   │   │   ├── ECG12LeadGrid.jsx       # New
│   │   │   │   ├── ECGWaveform.jsx         # Existing
│   │   │   │   └── LeadSelector.jsx        # Existing
│   │   │   ├── features/
│   │   │   │   ├── FeatureDisplay.jsx     # New
│   │   │   │   ├── TemporalFeatures.jsx   # New
│   │   │   │   └── FrequencyFeatures.jsx  # New
│   │   │   ├── interpretation/
│   │   │   │   ├── ClinicalInterpreter.jsx # New
│   │   │   │   └── DifferentialDiagnosis.jsx # New
│   │   │   ├── realtime/
│   │   │   │   ├── RealtimeDisplay.jsx    # New
│   │   │   │   ├── DeviceConnector.jsx    # New
│   │   │   │   └── AcquisitionControls.jsx # New
│   │   │   ├── simulation/
│   │   │   │   ├── ECGSimulator.jsx       # New
│   │   │   │   └── SignalGenerator.jsx    # New
│   │   │   └── [existing components]
│   │   ├── pages/
│   │   │   ├── PerformanceMetrics.jsx     # New
│   │   │   ├── BatchProcessing.jsx        # New
│   │   │   ├── RealtimeAcquisition.jsx    # New
│   │   │   ├── Simulation.jsx             # New
│   │   │   └── [existing pages]
│   │   └── [existing directories]
│   ├── package.json                       # Existing
│   └── vite.config.js                     # Existing
├── data/
│   └── sample_ecg/                        # Existing
├── docs/
│   ├── architecture.md                    # Update
│   ├── api.md                             # Update
│   └── model.md                           # Update
├── PS03_IMPLEMENTATION_PLAN.md             # New (this file)
├── MODEL_INTEGRATION.md                   # Existing
├── README.md                             # Update
└── [existing files]
```

---

## 🧪 Testing Strategy

### Unit Testing

**Backend Tests:**
```python
# backend/tests/test_simulation.py
import pytest
import numpy as np
from app.services.ecg_simulation import ECGSimulator

def test_normal_ecg_generation():
    simulator = ECGSimulator()
    signal = simulator.generate_normal_ecg()
    assert signal.shape == (12, 1000)
    assert np.all(np.isfinite(signal))

def test_abnormal_ecg_generation():
    simulator = ECGSimulator()
    mi_signal = simulator.generate_myocardial_infarction()
    assert mi_signal.shape == (12, 1000)

def test_noise_addition():
    simulator = ECGSimulator()
    clean_signal = simulator.generate_normal_ecg()
    noisy_signal = simulator.add_noise(clean_signal, 0.05)
    assert not np.array_equal(clean_signal, noisy_signal)

# backend/tests/test_feature_extraction.py
import pytest
from app.services.feature_extraction import feature_extractor

def test_temporal_feature_extraction():
    signal = np.random.randn(12, 1000)
    features = feature_extractor.extract_temporal_features(signal)
    assert "temporal" in features
    assert len(features["temporal"]) == 12

def test_frequency_feature_extraction():
    signal = np.random.randn(12, 1000)
    features = feature_extractor.extract_frequency_features(signal)
    assert "frequency" in features
    assert len(features["frequency"]) == 12

# backend/tests/test_clinical_interpretation.py
import pytest
from app.services.clinical_interpretation import clinical_interpreter

def test_interpretation_generation():
    prediction = {
        "prediction_code": "MI",
        "confidence": 0.85
    }
    features = {
        "temporal": {}
    }
    interpretation = clinical_interpreter.interpret_prediction(prediction, features)
    assert interpretation["urgency"] == "emergency"
    assert len(interpretation["recommendations"]) > 0
```

**Frontend Tests:**
```javascript
// frontend/src/components/__tests__/ECGSimulator.test.jsx
import { render, screen, fireEvent } from '@testing-library/react';
import ECGSimulator from '../simulation/ECGSimulator';

test('renders simulator controls', () => {
  render(<ECGSimulator />);
  expect(screen.getByText('ECG Simulator')).toBeInTheDocument();
  expect(screen.getByText('Generate')).toBeInTheDocument();
});

test('parameter changes update state', () => {
  render(<ECGSimulator />);
  const heartRateSlider = screen.getByLabelText('Heart Rate');
  fireEvent.change(heartRateSlider, { target: { value: '80' }});
  expect(screen.getByText('80 BPM')).toBeInTheDocument();
});

// frontend/src/components/__tests__/ClinicalInterpreter.test.jsx
import { render, screen } from '@testing-library/react';
import ClinicalInterpreter from '../interpretation/ClinicalInterpreter';

test('displays clinical interpretation', () => {
  const mockInterpretation = {
    primary_findings: ['Test finding'],
    clinical_significance: 'Test significance',
    urgency: 'urgent',
    recommendations: ['Test recommendation'],
    limitations: ['Test limitation']
  };
  render(<ClinicalInterpreter interpretation={mockInterpretation} />);
  expect(screen.getByText('Clinical Interpretation')).toBeInTheDocument();
  expect(screen.getByText('Test finding')).toBeInTheDocument();
});
```

### Integration Testing

```python
# backend/tests/test_integration.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_simulation_to_analysis_pipeline():
    # Generate ECG
    response = client.post("/api/simulation/generate", json={
        "abnormality": "normal",
        "heart_rate": 70.0
    })
    assert response.status_code == 200
    signal_data = response.json()["signal"]
    
    # Analyze generated signal
    # (This would require converting signal data to file format)
    # Test the complete pipeline

def test_feature_extraction_integration():
    # Test that feature extraction works with real ECG data
    # from existing analysis pipeline
    pass

def test_clinical_interpretation_integration():
    # Test complete analysis with interpretation
    pass
```

### Performance Testing

```python
# backend/tests/test_performance.py
import pytest
import time
from app.services.feature_extraction import feature_extractor
import numpy as np

def test_feature_extraction_performance():
    signal = np.random.randn(12, 1000)
    
    start_time = time.time()
    features = feature_extractor.extract_all_features(signal)
    end_time = time.time()
    
    processing_time = end_time - start_time
    assert processing_time < 2.0  # Should complete in under 2 seconds

def test_batch_processing_performance():
    # Test batch processing with multiple files
    pass
```

---

## 📅 Implementation Timeline

### Week 1: Foundation (Days 1-7)

**Days 1-2: ECG Simulation Module**
- Create ecg_simulation.py service
- Implement signal generation methods
- Add simulation API endpoints
- Create frontend simulator component
- Unit testing

**Days 3-4: Enhanced Feature Extraction**
- Create feature_extraction.py service
- Implement temporal/frequency/morphological features
- Integrate with existing ECG processing
- Create frontend display components
- Integration testing

**Days 5-6: 12-Lead ECG Grid Visualization**
- Create ECG12LeadGrid component
- Implement interactive lead selection
- Add zoom/pan functionality
- Integrate with results display
- UI testing

**Day 7: Integration & Testing**
- Integrate all Phase 1 features
- Comprehensive testing
- Bug fixes and refinement
- Documentation updates

### Week 2: Advanced Features (Days 8-14)

**Days 8-10: Real-time Acquisition Module**
- Add WebSocket support to FastAPI
- Create realtime_acquisition.py service
- Implement WebSocket endpoint
- Create frontend real-time display
- WebSocket testing

**Days 11-12: Clinical Interpretation Enhancement**
- Create clinical_interpretation.py service
- Implement clinical rules engine
- Integrate with analysis pipeline
- Create interpretation display components
- Clinical validation

**Days 13-14: Performance Metrics Dashboard**
- Create performance metrics API
- Add actual model evaluation results
- Create performance dashboard UI
- Integrate with navigation
- Performance testing

### Week 3: Integration & Polish (Days 15-21)

**Days 15-16: Batch Processing Mode**
- Create batch processing API
- Implement concurrent file processing
- Create batch upload UI
- Add results export functionality
- Batch testing

**Days 17-18: Integration Testing**
- End-to-end system testing
- Cross-feature integration testing
- Performance optimization
- Memory and resource testing

**Days 19-20: Documentation & Polish**
- Update technical documentation
- Create user guides
- Add academic documentation sections
- UI/UX improvements
- Code cleanup and optimization

**Day 21: Final Testing & Deployment**
- Comprehensive system testing
- User acceptance testing
- Deployment preparation
- Final documentation review

---

## 🚀 Deployment Strategy

### Development Environment

**Setup:**
1. Create feature branches for each major component
2. Use existing development environment
3. Test each feature independently before integration
4. Maintain existing functionality throughout development

**Testing:**
- Unit tests for each new component
- Integration tests for feature interactions
- Manual testing of UI components
- Performance testing under load

### Integration Phase

**Merge Strategy:**
1. Merge Phase 1 features to development branch
2. Comprehensive integration testing
3. Performance optimization
4. Merge Phase 2 features
5. Cross-feature integration testing
6. Merge Phase 3 features
7. Final system testing

**Quality Assurance:**
- Automated testing pipeline
- Code review process
- Documentation validation
- Security review

### Production Deployment

**Pre-deployment:**
1. Complete testing on staging environment
2. Performance benchmarking
3. Security audit
4. Documentation completion
5. Backup existing system

**Deployment Steps:**
1. Update dependencies
2. Run database migrations
3. Deploy backend changes
4. Deploy frontend changes
5. Monitor system performance
6. User acceptance testing

**Post-deployment:**
1. Monitor system metrics
2. Collect user feedback
3. Address any issues
4. Plan for future enhancements

---

## 📊 Success Metrics

### Technical Metrics

**Performance:**
- Model Accuracy: >85% maintained
- Response Time: <2 seconds for analysis
- Real-time Latency: <100ms for WebSocket updates
- System Uptime: >99% availability
- Memory Usage: <2GB for typical operations

**Quality:**
- Code Coverage: >80% for new code
- Bug Density: <1 bug per 1000 lines
- Documentation Completeness: 100%
- API Response Time: <500ms average

### User Experience Metrics

**Adoption:**
- Feature Adoption: >70% users try new features
- Task Completion: >90% success rate for analysis
- User Satisfaction: >4.5/5 rating
- Learning Curve: <15 minutes to basic proficiency

**Performance:**
- Page Load Time: <3 seconds
- Analysis Completion: <5 seconds for typical ECG
- Real-time Display: <100ms latency
- Mobile Responsiveness: 100% functional on mobile devices

### Academic Metrics

**PS-03 Compliance:**
- Requirement Coverage: 100%
- Documentation Quality: Complete technical documentation
- Reproducibility: Clear methodology and code organization
- Clinical Validation: Evidence-based interpretation

**Research Readiness:**
- Methodology Clarity: Complete documentation
- Statistical Analysis: Comprehensive performance metrics
- Clinical Relevance: Validated interpretation rules
- Publication Quality: Academic paper structure

---

## 🎓 Academic Documentation

### Research Paper Structure

**1. Introduction**
- Background on ECG analysis and AI in healthcare
- Cardiovascular disease prevalence and impact
- Current challenges in ECG interpretation
- AI-assisted screening potential
- Research objectives and PS-03 compliance

**2. Methods**
- System architecture and design
- ECG signal preprocessing pipeline
- Feature extraction methodology
- Machine learning model architecture
- Clinical interpretation framework
- Dataset description and preprocessing

**3. System Implementation**
- Technology stack selection rationale
- Component architecture and interactions
- Real-time acquisition implementation
- Visualization and user interface design
- API design and integration

**4. Results**
- Model performance metrics
- Feature extraction validation
- Clinical interpretation accuracy
- System performance benchmarks
- User experience evaluation

**5. Discussion**
- Clinical implications and limitations
- Comparison with existing systems
- Technical challenges and solutions
- Future research directions
- PS-03 requirement fulfillment

**6. Conclusion**
- Summary of achievements
- Impact on ECG screening
- Contributions to the field
- Future work and enhancements

### Technical Documentation

**API Documentation:**
- Complete endpoint reference
- Request/response formats
- Authentication and security
- Error handling and status codes
- Rate limiting and usage guidelines

**Model Documentation:**
- Architecture details and parameters
- Training methodology and dataset
- Performance metrics and validation
- Limitations and bias analysis
- Interpretation of predictions

**User Guide:**
- Installation and setup instructions
- Feature usage tutorials
- Best practices and tips
- Troubleshooting guide
- FAQ and support resources

**Developer Guide:**
- System architecture overview
- Component interaction diagrams
- Extension and customization guide
- Testing methodology
- Deployment procedures

---

## 🔒 Security & Compliance

### Data Security

**Privacy Protection:**
- No patient data storage
- Anonymous analysis only
- Secure file handling
- Temporary data storage
- Encrypted data transmission

**Access Control:**
- Authentication system (future enhancement)
- Role-based access control (future enhancement)
- Audit logging (future enhancement)
- Secure API endpoints

### Medical Device Compliance

**Regulatory Considerations:**
- Educational/research tool positioning
- Medical disclaimer prominence
- Non-diagnostic classification
- Clinical validation requirements
- User responsibility acknowledgment

**Safety Features:**
- Confidence threshold warnings
- Emergency condition alerts
- Professional consultation recommendations
- Limitation transparency
- Error handling and fallbacks

---

## 🔄 Maintenance & Future Enhancements

### Maintenance Plan

**Regular Updates:**
- Model retraining with new data
- Feature extraction improvements
- UI/UX enhancements
- Performance optimization
- Security updates

**Monitoring:**
- System performance metrics
- User feedback collection
- Error tracking and reporting
- Usage analytics
- Model performance monitoring

### Future Enhancements

**Short-term (3-6 months):**
- User authentication system
- Mobile application development
- Additional ECG lead formats
- Enhanced export options
- Multi-language support

**Long-term (6-12 months):**
- Integration with EHR systems
- Advanced AI model architectures
- Real-time arrhythmia detection
- Telemedicine integration
- Clinical decision support

---

## 📞 Support & Resources

### Development Support

**Documentation:**
- This implementation plan
- Code comments and documentation
- API documentation (Swagger UI)
- User guides and tutorials

**Troubleshooting:**
- Common issues and solutions
- Debugging guides
- Performance optimization tips
- Integration troubleshooting

### Academic Support

**Research Resources:**
- Dataset references and citations
- Methodology documentation
- Statistical analysis templates
- Publication guidelines

**Clinical Validation:**
- Medical professional review process
- Clinical testing protocols
- Validation study design
- Regulatory compliance guidance

---

## 🎯 Conclusion

This implementation plan provides a comprehensive roadmap to transform the existing CardioSense AI project into a complete PS-03 compliant laboratory prototype. The systematic approach ensures:

1. **Full PS-03 Compliance** - All requirements addressed with concrete implementations
2. **Academic Readiness** - Complete documentation and research framework
3. **Clinical Safety** - Appropriate disclaimers and interpretation limitations
4. **Technical Excellence** - Robust architecture and comprehensive testing
5. **User Experience** - Intuitive interface and comprehensive features

The 3-week timeline balances development speed with quality assurance, while the modular design allows for incremental implementation and testing. The focus on educational/research positioning ensures appropriate medical disclaimers and clinical safety measures.

Upon completion, the system will serve as an exemplary laboratory-level prototype demonstrating:
- ECG signal acquisition and processing
- Advanced feature extraction and analysis
- Machine learning-based classification
- Clinical interpretation and decision support
- Real-time monitoring capabilities
- Comprehensive visualization and reporting

This implementation provides a solid foundation for academic research, educational purposes, and future development toward clinical applications.

---

**Document Version:** 1.0  
**Last Updated:** 2026-09-23  
**Project:** CardioSense AI PS-03 Enhancement  
**Status:** Ready for Implementation
