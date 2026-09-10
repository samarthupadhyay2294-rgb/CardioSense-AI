import time
import torch
import numpy as np
from typing import Dict, List, Tuple, Optional
import json

from app.ml.model import model_loader
from app.ml.preprocessing import preprocess_signal, validate_signal, signal_to_tensor


class ECGPredictor:
    def __init__(self):
        self.model = None
        self.config = None
        self.device = None
        self.thresholds = None
        self.classes = None
        self.class_names = None
        self._initialize()

    def _initialize(self):
        self.model = model_loader.get_model()
        self.config = model_loader.get_config()
        self.device = model_loader.get_device()
        self.thresholds = self.config.get("thresholds", {})
        self.classes = self.config.get("classes", ["NORM", "MI", "STTC", "CD", "HYP"])
        self.class_names = self.config.get("class_names", {})

    def preprocess(self, signal: np.ndarray) -> torch.Tensor:
        return signal_to_tensor(signal)

    def predict(self, signal: np.ndarray) -> Dict:
        start_time = time.time()
        
        is_valid, msg = validate_signal(signal)
        if not is_valid:
            raise ValueError(f"Signal validation failed: {msg}")
        
        input_tensor = self.preprocess(signal).to(self.device)
        
        with torch.no_grad():
            logits = self.model(input_tensor)
            probs = torch.sigmoid(logits).cpu().numpy()[0]
        
        predictions = {}
        for i, cls in enumerate(self.classes):
            threshold = self.thresholds.get(cls, 0.5)
            predictions[cls] = bool(probs[i] >= threshold)
        
        positive_classes = [cls for cls, pred in predictions.items() if pred]
        
        if not positive_classes:
            main_prediction = "NORM"
            confidence = 1.0 - probs[self.classes.index("NORM")]
        else:
            main_prediction = max(positive_classes, key=lambda c: probs[self.classes.index(c)])
            confidence = float(probs[self.classes.index(main_prediction)])
        
        probabilities = {self.class_names.get(cls, cls): float(probs[i]) for i, cls in enumerate(self.classes)}
        
        processing_time = time.time() - start_time
        
        return {
            "prediction": self.class_names.get(main_prediction, main_prediction),
            "prediction_code": main_prediction,
            "confidence": round(confidence, 4),
            "probabilities": probabilities,
            "all_predictions": {self.class_names.get(cls, cls): pred for cls, pred in predictions.items()},
            "model_version": self.config.get("model_version", "1.0"),
            "processing_time": round(processing_time, 4)
        }

    def predict_batch(self, signals: List[np.ndarray]) -> List[Dict]:
        return [self.predict(sig) for sig in signals]


predictor = ECGPredictor()