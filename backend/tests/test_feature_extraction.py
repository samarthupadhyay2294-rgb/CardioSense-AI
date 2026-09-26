import pytest
import numpy as np
from app.services.feature_extraction import ECGFeatureExtractor


def test_temporal_feature_extraction():
    """Test temporal feature extraction."""
    extractor = ECGFeatureExtractor()
    signal = np.random.randn(12, 1000)
    
    features = extractor.extract_temporal_features(signal)
    
    # extract_temporal_features returns dict with lead names as keys
    assert len(features) == 12
    assert "II" in features  # Standard lead name


def test_frequency_feature_extraction():
    """Test frequency feature extraction."""
    extractor = ECGFeatureExtractor()
    signal = np.random.randn(12, 1000)
    
    features = extractor.extract_frequency_features(signal)
    
    # extract_frequency_features returns dict with lead names as keys
    assert len(features) == 12
    assert "II" in features
    
    # Check frequency features exist
    lead_features = features["II"]
    assert "dominant_frequency" in lead_features
    assert "spectral_entropy" in lead_features
    assert "band_power" in lead_features
    assert "total_power" in lead_features


def test_morphological_feature_extraction():
    """Test morphological feature extraction."""
    extractor = ECGFeatureExtractor()
    signal = np.random.randn(12, 1000)
    
    features = extractor.extract_morphological_features(signal)
    
    # extract_morphological_features returns dict with lead names as keys
    assert len(features) == 12
    assert "II" in features
    
    # Check morphological features exist
    lead_features = features["II"]
    assert "mean" in lead_features
    assert "std" in lead_features
    assert "skewness" in lead_features
    assert "kurtosis" in lead_features
    assert "zero_crossings" in lead_features
    assert "rms" in lead_features


def test_all_features_extraction():
    """Test extraction of all feature types."""
    extractor = ECGFeatureExtractor()
    signal = np.random.randn(12, 1000)
    
    features = extractor.extract_all_features(signal)
    
    assert "temporal" in features
    assert "frequency" in features
    assert "morphological" in features


def test_r_peak_detection():
    """Test R peak detection."""
    extractor = ECGFeatureExtractor()
    # Create a simple signal with peaks
    signal = np.zeros(1000)
    signal[100] = 1.0
    signal[200] = 1.0
    signal[300] = 1.0
    
    peaks = extractor.detect_r_peaks(signal)
    
    assert len(peaks) > 0
    assert all(0 <= p < len(signal) for p in peaks)


def test_rr_intervals():
    """Test RR interval calculation."""
    extractor = ECGFeatureExtractor()
    r_peaks = np.array([100, 200, 300])
    
    rr_intervals = extractor.extract_rr_intervals(r_peaks)
    
    assert len(rr_intervals) == 2
    assert all(rr > 0 for rr in rr_intervals)


def test_heart_rate_calculation():
    """Test heart rate calculation."""
    extractor = ECGFeatureExtractor()
    rr_intervals = [0.8, 0.9, 0.85]  # seconds
    
    hr = extractor.calculate_heart_rate(rr_intervals)
    
    assert "mean" in hr
    assert "min" in hr
    assert "max" in hr
    assert "std" in hr
    assert hr["mean"] > 0


def test_empty_signal_handling():
    """Test handling of empty signals."""
    extractor = ECGFeatureExtractor()
    empty_signal = np.array([]).reshape(0, 1000)
    
    # Should handle gracefully
    features = extractor.extract_temporal_features(empty_signal)
    assert isinstance(features, dict)


def test_invalid_signal_shape():
    """Test handling of invalid signal shapes."""
    extractor = ECGFeatureExtractor()
    # Wrong number of leads
    signal = np.random.randn(8, 1000)
    
    features = extractor.extract_temporal_features(signal)
    # Should still work but with fewer leads
    assert len(features) == 8


def test_lead_names():
    """Test that standard lead names are used."""
    extractor = ECGFeatureExtractor()
    expected_leads = ["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"]
    
    assert extractor.lead_names == expected_leads


def test_frequency_bands():
    """Test that frequency bands are correctly defined."""
    extractor = ECGFeatureExtractor()
    signal = np.random.randn(12, 1000)
    
    features = extractor.extract_frequency_features(signal)
    lead_features = features["II"]
    
    # Check that standard frequency bands exist
    expected_bands = ["very_low", "low", "medium", "high"]
    for band in expected_bands:
        assert band in lead_features["band_power"]


def test_statistical_calculations():
    """Test statistical calculations are reasonable."""
    extractor = ECGFeatureExtractor()
    signal = np.random.randn(12, 1000)
    
    features = extractor.extract_morphological_features(signal)
    lead_features = features["II"]
    
    # Mean should be close to 0 for random normal data
    assert abs(lead_features["mean"]) < 1.0
    # Std should be around 1 for random normal data
    assert 0.5 < lead_features["std"] < 2.0
    # RMS should be positive
    assert lead_features["rms"] > 0