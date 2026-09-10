import torch
import json
from pathlib import Path

checkpoint_path = Path("models/image/best_model.pt")
config_path = Path("models/image/model_config.json")

# Load config
with open(config_path) as f:
    config = json.load(f)
print("Config loaded, classes:", config["classes"])
print("Class mapping:", config["class_mapping"])

# Load checkpoint
ckpt = torch.load(checkpoint_path, map_location="cpu")
print("Checkpoint type:", type(ckpt))
if isinstance(ckpt, dict):
    print("Keys:", list(ckpt.keys()))
if "model_state_dict" in ckpt:
    print("model_state_dict keys (first 5):", list(ckpt["model_state_dict"].keys())[:5])
if "epoch" in ckpt:
    print("epoch:", ckpt["epoch"])
if "best_metric" in ckpt:
    print("best_metric:", ckpt["best_metric"])

# Try to create model and load state dict
from torchvision.models import efficientnet_b0
model = efficientnet_b0(weights=None)
in_features = model.classifier[1].in_features
print("Original in_features:", in_features)

num_classes = len(config["class_mapping"])
model.classifier[1] = torch.nn.Linear(in_features, num_classes)
print("New num_classes:", num_classes)

try:
    model.load_state_dict(ckpt["model_state_dict"])
    print("Model loaded successfully!")
    model.eval()
    
    # Try a forward pass
    import numpy as np
    from PIL import Image
    img = Image.new("RGB", (224, 224))
    tensor = torch.zeros(1, 3, 224, 224)
    with torch.no_grad():
        outputs = model(tensor)
        probs = torch.softmax(outputs, dim=1).squeeze().cpu().numpy()
        pred_idx = int(np.argmax(probs))
        confidence = float(probs[pred_idx])
        print("Prediction index:", pred_idx)
        print("Confidence:", confidence)
        print("Predicted class:", config["class_mapping"].get(str(pred_idx), "unknown"))
except Exception as e:
    print("Error during model load/predict:", e)
    import traceback
    traceback.print_exc()