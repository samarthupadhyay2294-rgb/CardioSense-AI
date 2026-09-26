import pytest
import numpy as np
from app.services.ecg_simulation import ecg_simulator
from app.services.feature_extraction import feature_extractor
from app.ml.predictor import predictor


def test_simulation_to_feature_extraction():
    """Test integration between simulator and feature extraction."""
    # Generate simulated ECG
    signal = ecg_simulator.generate_normal_ecg()
    
    # Extract features
    features = feature_extractor.extract_all_features(signal)
    
    # Verify features were extracted
    assert "temporal" in features
    assert "frequency" in features
    assert "morphological" in features
    assert len(features["temporal"]) == 12


def test_simulation_to_ml_pipeline():
    """Test integration between simulator and ML pipeline."""
    # Generate simulated ECG
    signal = ecg_simulator.generate_normal_ecg()
    
    # Run through ML predictor
    prediction = predictor.predict(signal)
    
    # Verify prediction structure
    assert "prediction" in prediction
    assert "prediction_code" in prediction
    assert "confidence" in prediction
    assert "probabilities" in prediction
    assert prediction["confidence"] >= 0
    assert prediction["confidence"] <= 1


def test_full_pipeline_integration():
    """Test complete pipeline: simulation -> features -> ML."""
    # Generate different abnormality types
    abnormality_types = ["normal", "MI", "STTC", "CD", "HYP"]
    
    for abnormality in abnormality_types:
        # Generate signal
        signal = ecg_simulator.generate_custom_ecg({
            "abnormality": abnormality,
            "heart_rate": 70,
            "noise_level": 0.0,
            "baseline_wander": False,
            "duration": 10
        })
        
        # Extract features
        features = feature_extractor.extract_all_features(signal)
        
        # Run ML prediction
        prediction = predictor.predict(signal)
        
        # Verify all components work
        assert signal.shape == (12, 1000)
        assert "temporal" in features
        assert "prediction" in prediction


def test_signal_format_consistency():
    """Test that signal format is consistent across pipeline."""
    # Generate signal
    signal = ecg_simulator.generate_normal_ecg()
    
    # Verify standard format
    assert signal.shape[0] == 12  # 12 leads
    assert signal.shape[1] == 1000  # 1000 samples at 100 Hz for 10 seconds
    assert signal.dtype in [np.float32, np.float64]
    
    # Verify it works with feature extractor
    features = feature_extractor.extract_all_features(signal)
    assert len(features["temporal"]) == 12
    
    # Verify it works with ML predictor
    prediction = predictor.predict(signal)
    assert "prediction" in prediction


def test_noise_integration():
    """Test that noisy signals still work through pipeline."""
    # Generate clean signal
    clean_signal = ecg_simulator.generate_normal_ecg()
    
    # Add noise
    noisy_signal = ecg_simulator.add_noise(clean_signal, 0.05)
    
    # Both should work through pipeline
    clean_features = feature_extractor.extract_all_features(clean_signal)
    noisy_features = feature_extractor.extract_all_features(noisy_signal)
    
    clean_prediction = predictor.predict(clean_signal)
    noisy_prediction = predictor.predict(noisy_signal)
    
    assert "temporal" in clean_features
    assert "temporal" in noisy_features
    assert "prediction" in clean_prediction
    assert "prediction" in noisy_prediction


def test_different_heart_rates_pipeline():
    """Test pipeline with different heart rates."""
    heart_rates = [50, 70, 100]
    
    for hr in heart_rates:
        signal = ecg_simulator.generate_normal_ecg(heart_rate=hr)
        
        # Should work with feature extraction
        features = feature_extractor.extract_all_features(signal)
        assert "temporal" in features
        
        # Should work with ML prediction
        prediction = predictor.predict(signal)
        assert "prediction" in prediction


def test_estimation_flags():
    """Test that estimated features are properly flagged."""
    signal = ecg_simulator.generate_normal_ecg()
    features = feature_extractor.extract_temporal_features(signal)
    
    # Check that QRS and ST features are marked as estimated
    for lead_name, lead_features in features.items():
        if "qrs_features" in lead_features:
            assert lead_features["qrs_features"].get("estimated") == True
        if "st_segment" in lead_features:
            assert lead_features["st_segment"].get("estimated") == True