
import torch
import torchvision.transforms as T

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]
IMG_SIZE = 224

class AddGaussianNoise:
    def __init__(self, std=0.02, p=0.2):
        self.std = std
        self.p = p
    def __call__(self, tensor):
        if torch.rand(1).item() < self.p:
            return tensor + torch.randn_like(tensor) * self.std
        return tensor

# ECG-safe augmentation: NO horizontal/vertical flips and NO extreme rotation —
# waveform orientation and shape are diagnostically meaningful.
train_transforms = T.Compose([
    T.Resize((IMG_SIZE + 20, IMG_SIZE + 20)),
    T.RandomCrop(IMG_SIZE),
    T.RandomAffine(degrees=5, translate=(0.03, 0.03)),
    T.ColorJitter(brightness=0.15, contrast=0.15),
    T.RandomApply([T.GaussianBlur(kernel_size=3, sigma=(0.1, 1.0))], p=0.2),
    T.ToTensor(),
    AddGaussianNoise(std=0.02, p=0.2),
    T.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
])

eval_transforms = T.Compose([
    T.Resize((IMG_SIZE + 20, IMG_SIZE + 20)),
    T.CenterCrop(IMG_SIZE),
    T.ToTensor(),
    T.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
])
