
import json
import numpy as np
import torch
from PIL import Image, UnidentifiedImageError

CONFIDENCE_THRESHOLD = 0.60

class ECGImagePredictor:
    def __init__(self, checkpoint_path, config_path, device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        with open(config_path) as f:
            self.config = json.load(f)
        self.class_mapping = self.config["class_mapping"]
        self.idx_to_class = {v: k for k, v in self.class_mapping.items()}
        self.model_name = self.config["model_name"]
        self.model_version = self.config["model_version"]
        self.input_size = tuple(self.config["input_size"])
        self.mean = self.config["normalization"]["mean"]
        self.std = self.config["normalization"]["std"]
        self.model = self._load_model(checkpoint_path)

    def _load_model(self, checkpoint_path):
        from model import create_model
        model = create_model(num_classes=len(self.class_mapping), pretrained=False)
        ckpt = torch.load(checkpoint_path, map_location=self.device)
        model.load_state_dict(ckpt["model_state_dict"])
        model.to(self.device)
        model.eval()
        return model

    def preprocess(self, image: Image.Image):
        import torchvision.transforms as T
        tfm = T.Compose([
            T.Resize((self.input_size[0] + 20, self.input_size[1] + 20)),
            T.CenterCrop(self.input_size),
            T.ToTensor(),
            T.Normalize(mean=self.mean, std=self.std),
        ])
        return tfm(image.convert("RGB")).unsqueeze(0)

    def predict(self, image: Image.Image):
        tensor = self.preprocess(image).to(self.device)
        with torch.no_grad():
            outputs = self.model(tensor)
            probs = torch.softmax(outputs, dim=1).squeeze().cpu().numpy()
        pred_idx = int(np.argmax(probs))
        confidence = float(probs[pred_idx])

        result = {
            "prediction": self.idx_to_class[pred_idx],
            "confidence": confidence,
            "probabilities": {self.idx_to_class[i]: float(p) for i, p in enumerate(probs)},
            "model_name": self.model_name,
            "model_version": self.model_version,
        }
        if confidence < CONFIDENCE_THRESHOLD:
            result["warning"] = ("Low model confidence. The ECG image may be difficult "
                                  "to classify reliably.")
        return result

    def predict_from_path(self, path):
        import os
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        ext = os.path.splitext(path)[1].lower()
        if ext not in (".png", ".jpg", ".jpeg"):
            raise ValueError(f"Unsupported file type: {ext}. Expected PNG, JPG, or JPEG.")
        try:
            img = Image.open(path)
            img.verify()
            img = Image.open(path)  # reopen after verify()
        except UnidentifiedImageError:
            raise ValueError(f"File is not a readable image: {path}")
        except Exception as e:
            raise ValueError(f"Corrupted or unreadable image ({path}): {e}")
        return self.predict(img)

    def generate_gradcam(self, image: Image.Image):
        from gradcam import GradCAM, overlay_heatmap
        cam_engine = GradCAM(self.model)
        tensor = self.preprocess(image).to(self.device)
        cam, pred_idx, probs = cam_engine.generate(tensor)
        overlay = overlay_heatmap(image.convert("RGB"), cam)
        return overlay, self.idx_to_class[pred_idx], float(probs[pred_idx])
