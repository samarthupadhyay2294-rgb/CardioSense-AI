import torch
import numpy as np
from typing import Dict, List, Optional
import torch.nn.functional as F

from app.ml.model import model_loader
from app.ml.predictor import predictor


class ExplainabilityEngine:
    def __init__(self):
        self.model = model_loader.get_model()
        self.device = model_loader.get_device()
        self.classes = predictor.classes

    def integrated_gradients(
        self,
        input_tensor: torch.Tensor,
        target_class_idx: int,
        steps: int = 50
    ) -> np.ndarray:
        baseline = torch.zeros_like(input_tensor).to(self.device)
        input_tensor = input_tensor.to(self.device)
        
        alphas = torch.linspace(0, 1, steps).to(self.device)
        integrated_grads = torch.zeros_like(input_tensor)
        
        for alpha in alphas:
            interpolated = baseline + alpha * (input_tensor - baseline)
            interpolated.requires_grad_(True)
            
            logits = self.model(interpolated)
            target_logit = logits[0, target_class_idx]
            
            self.model.zero_grad()
            target_logit.backward(retain_graph=True)
            
            grads = interpolated.grad.clone()
            integrated_grads += grads
        
        integrated_grads = integrated_grads / steps
        integrated_grads = integrated_grads * (input_tensor - baseline)
        
        return integrated_grads.squeeze(0).cpu().numpy()

    def saliency_map(self, input_tensor: torch.Tensor, target_class_idx: int) -> np.ndarray:
        input_tensor = input_tensor.to(self.device).requires_grad_(True)
        
        logits = self.model(input_tensor)
        target_logit = logits[0, target_class_idx]
        
        self.model.zero_grad()
        target_logit.backward()
        
        saliency = input_tensor.grad.abs().squeeze(0).cpu().numpy()
        return saliency

    def get_attribution(
        self,
        signal: np.ndarray,
        target_class: str,
        method: str = "integrated_gradients"
    ) -> Dict:
        from app.ml.preprocessing import signal_to_tensor
        
        if target_class not in self.classes:
            raise ValueError(f"Unknown class: {target_class}")
        
        target_idx = self.classes.index(target_class)
        input_tensor = signal_to_tensor(signal)
        
        if method == "integrated_gradients":
            attribution = self.integrated_gradients(input_tensor, target_idx)
        elif method == "saliency":
            attribution = self.saliency_map(input_tensor, target_idx)
        else:
            raise ValueError(f"Unknown method: {method}")
        
        attribution_per_lead = np.abs(attribution).mean(axis=1)
        total = attribution_per_lead.sum()
        if total > 0:
            attribution_normalized = (attribution_per_lead / total).tolist()
        else:
            attribution_normalized = [1.0 / len(attribution_per_lead)] * len(attribution_per_lead)
        
        time_attribution = np.abs(attribution).mean(axis=0)
        time_total = time_attribution.sum()
        if time_total > 0:
            time_normalized = (time_attribution / time_total).tolist()
        else:
            time_normalized = [1.0 / len(time_attribution)] * len(time_attribution)
        
        return {
            "method": method,
            "target_class": target_class,
            "lead_importance": dict(zip(
                ["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"],
                attribution_normalized
            )),
            "time_importance": time_normalized
        }


explainability_engine = ExplainabilityEngine()