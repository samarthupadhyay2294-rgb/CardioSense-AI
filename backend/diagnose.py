import sys
import torch
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, '.')

checkpoint_path = Path("models/image/best_model.pt")
config_path = Path("models/image/model_config.json")

print("=" * 60)
print("IMAGE MODEL DIAGNOSTIC")
print("=" * 60)

# 1. Check files exist
print("\n1. FILE EXISTENCE:")
print("   Checkpoint exists:", checkpoint_path.exists())
print(f"   Config exists: {config_path.exists()}")

# 2. Load and inspect config
print("\n2. CONFIG INSPECTION:")
with open(config_path) as f:
    config = json.load(f)
print(f"   Model name: {config['model_name']}")
print(f"   Input size: {config['input_size']}")
print(f"   Number of classes: {len(config['classes'])}")
print(f"   Classes: {config['classes']}")
print(f"   Class mapping (first 5): {list(config['class_mapping'].items())[:5]}")
print(f"   Normalization mean: {config['normalization']['mean']}")
print(f"   Normalization std: {config['normalization']['std']}")

# 3. Load and inspect checkpoint
print("\n3. CHECKPOINT INSPECTION:")
ckpt = torch.load(checkpoint_path, map_location='cpu')
print(f"   Checkpoint type: {type(ckpt)}")
if isinstance(ckpt, dict):
    print(f"   Keys: {list(ckpt.keys())}")
    for k in ckpt.keys():
        print(f"   - {k}: shape={ckpt[k].shape if hasattr(ckpt[k], 'shape') else 'N/A'}")
    
    # Check for model_state_dict
    if "model_state_dict" in ckpt:
        msd = ckpt["model_state_dict"]
        print(f"   model_state_dict type: {type(msd)}")
        print(f"   model_state_dict keys (first 5): {list(msd.keys())[:5]}")
        print(f"   model_state_dict sample: {list(msd.values())[:5]}")
    
    # Check for epoch
    if "epoch" in ckpt:
        print(f"   epoch: {ckpt['epoch']}")
    if "best_metric" in ckpt:
        print(f"   best_metric: {ckpt['best_metric']}")
    
    # Check classifier key
    for k in ckpt.keys():
        if "classifier" in k.lower() or "fc" in k.lower():
            print(f"   Found relevant key: {k} shape={ckpt[k].shape if hasattr(ckpt[k], 'shape') else 'N/A'}")

# 4. Try to load model
print("\n4. MODEL LOADING TEST:")
try:
    from torchvision.models import efficientnet_b0
    model = efficientnet_b0(weights=None)
    in_features = model.classifier[1].in_features
    print(f"   Original classifier in_features: {in_features}")
    
    num_classes = len(config["class_mapping"])
    model.classifier[1] = torch.nn.Linear(in_features, num_classes)
    print(f"   New num_classes: {num_classes}")
    
    model.load_state_dict(ckpt["model_state_dict"])
    print("   ✓ Model state dict loaded successfully")
    model.eval()
    
    # Try inference
    import numpy as np
    from PIL import Image
    img = Image.new("RGB", (224, 224))
    tensor = torch.zeros(1, 3, 224, 224)
    with torch.no_grad():
        outputs = model(tensor)
        probs = torch.softmax(outputs, dim=1).squeeze().cpu().numpy()
        pred_idx = int(np.argmax(probs))
        confidence = float(probs[pred_idx])
        print(f"   ✓ Inference successful!")
        print(f"   Predicted index: {pred_idx}")
        print(f"   Confidence: {confidence:.4f}")
        # Map to class
        idx_to_class = {v: k for k, v in config["class_mapping"].items()}
        print(f"   Predicted class: {idx_to_class.get(pred_idx, 'unknown')}")
        
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()