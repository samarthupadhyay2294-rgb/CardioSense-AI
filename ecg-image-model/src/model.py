
import torch.nn as nn
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights

def create_model(num_classes: int, pretrained: bool = True):
    weights = EfficientNet_B0_Weights.IMAGENET1K_V1 if pretrained else None
    model = efficientnet_b0(weights=weights)
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features, num_classes)
    return model

def freeze_backbone(model):
    for param in model.features.parameters():
        param.requires_grad = False

def unfreeze_last_blocks(model, n_blocks=3):
    # model.features is a Sequential of stages; unfreeze the last n_blocks stages
    stages = list(model.features.children())
    for stage in stages[-n_blocks:]:
        for param in stage.parameters():
            param.requires_grad = True
