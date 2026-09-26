import pytest
import numpy as np
from app.services.ecg_simulation import ECGSimulator


def test_normal_ecg_generation():
    """Test normal ECG signal generation."""
    simulator = ECGSimulator()
    signal = simulator.generate_normal_ecg()
    
    assert signal.shape == (12, 1000)
    assert np.all(np.isfinite(signal))
    assert signal.dtype == np.float64


def test_mi_ecg_generation():
    """Test myocardial infarction ECG generation."""
    simulator = ECGSimulator()
    signal = simulator.generate_myocardial_infarction()
    
    assert signal.shape == (12, 1000)
    assert np.all(np.isfinite(signal))


def test_sttc_ecg_generation():
    """Test ST/T changes ECG generation."""
    simulator = ECGSimulator()
    signal = simulator.generate_sttc()
    
    assert signal.shape == (12, 1000)
    assert np.all(np.isfinite(signal))


def test_cd_ecg_generation():
    """Test conduction disturbance ECG generation."""
    simulator = ECGSimulator()
    signal = simulator.generate_conduction_disturbance()
    
    assert signal.shape == (12, 1000)
    assert np.all(np.isfinite(signal))


def test_hypertrophy_ecg_generation():
    """Test hypertrophy ECG generation."""
    simulator = ECGSimulator()
    signal = simulator.generate_hypertrophy()
    
    assert signal.shape == (12, 1000)
    assert np.all(np.isfinite(signal))


def test_noise_addition():
    """Test noise addition to ECG signal."""
    simulator = ECGSimulator()
    clean_signal = simulator.generate_normal_ecg()
    noisy_signal = simulator.add_noise(clean_signal, 0.05)
    
    assert not np.array_equal(clean_signal, noisy_signal)
    assert noisy_signal.shape == clean_signal.shape


def test_baseline_wander():
    """Test baseline wander addition."""
    simulator = ECGSimulator()
    clean_signal = simulator.generate_normal_ecg()
    wander_signal = simulator.add_baseline_wander(clean_signal)
    
    assert not np.array_equal(clean_signal, wander_signal)
    assert wander_signal.shape == clean_signal.shape


def test_different_heart_rates():
    """Test ECG generation with different heart rates."""
    simulator = ECGSimulator()
    
    for hr in [50, 70, 100]:
        signal = simulator.generate_normal_ecg(heart_rate=hr)
        assert signal.shape == (12, 1000)
        assert np.all(np.isfinite(signal))


def test_different_durations():
    """Test ECG generation with different durations."""
    simulator = ECGSimulator(duration=5.0)
    signal = simulator.generate_normal_ecg()
    
    assert signal.shape == (12, 500)  # 100 Hz * 5 seconds = 500 samples


def test_custom_ecg_generation():
    """Test custom ECG generation with parameters."""
    simulator = ECGSimulator()
    params = {
        "abnormality": "normal",
        "heart_rate": 80,
        "noise_level": 0.05,
        "baseline_wander": False,
        "duration": 10
    }
    
    signal = simulator.generate_custom_ecg(params)
    assert signal.shape == (12, 1000)
    assert np.all(np.isfinite(signal))


def test_invalid_heart_rate():
    """Test validation of invalid heart rate."""
    simulator = ECGSimulator()
    
    with pytest.raises(ValueError, match="Heart rate must be between"):
        simulator.generate_normal_ecg(heart_rate=250)


def test_invalid_duration():
    """Test validation of invalid duration."""
    simulator = ECGSimulator(duration=100)
    
    with pytest.raises(ValueError, match="Duration must be between"):
        simulator.generate_normal_ecg()


def test_invalid_abnormality():
    """Test validation of invalid abnormality type."""
    simulator = ECGSimulator()
    params = {
        "abnormality": "invalid_type",
        "heart_rate": 70,
        "noise_level": 0.0,
        "baseline_wander": False,
        "duration": 10
    }
    
    with pytest.raises(ValueError, match="Invalid abnormality"):
        simulator.generate_custom_ecg(params)


def test_lead_names():
    """Test that standard lead names are used."""
    simulator = ECGSimulator()
    expected_leads = ["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"]
    
    assert simulator.lead_names == expected_leads