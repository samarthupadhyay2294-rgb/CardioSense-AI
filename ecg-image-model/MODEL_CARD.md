# MODEL CARD — CardioSense AI ECG Image Classifier

## Model name
EfficientNet-B0 (ECG Image Classifier)

## Architecture
EfficientNet-B0, ImageNet-pretrained, transfer-learned with a two-stage
schedule (frozen backbone -> partial fine-tuning of the last 3 stages).

## Dataset
Source: user-provided Kaggle ECG image dataset (`D:/Personal/model1/image.zip`).
Total images: 54613
Classes (15): A, E, F, J, L, N, Q, R, S, V, aa, e, f, j, p
Corrupted images excluded: 0

## Task
Multi-class classification of ECG images.

## Input format
PNG, JPG, JPEG. Converted to RGB, resized/center-cropped to 224x224,
ImageNet-normalized.

## Input resolution
224 x 224

## Classes
['A', 'E', 'F', 'J', 'L', 'N', 'Q', 'R', 'S', 'V', 'aa', 'e', 'f', 'j', 'p']

## Training procedure
Stage 1: frozen backbone, classification head only, 8 max epochs, lr=0.0001.
Stage 2: last 3 backbone stages unfrozen, fine-tuned, 12 max epochs, lr=1e-05.
Optimizer: AdamW, weight_decay=0.0001. Mixed precision (AMP) used on GPU.
Early stopping patience: 5 epochs (on validation Macro F1).

## Augmentation (ECG-safe)
Small rotation/translation (RandomAffine), mild brightness/contrast jitter,
occasional mild Gaussian blur and low-magnitude Gaussian noise.
No flips and no extreme rotation/perspective — ECG waveform orientation and
shape are diagnostically meaningful.

## Class imbalance strategy
Compared weighted cross-entropy vs. WeightedRandomSampler on validation
Macro F1; selected: **weighted_random_sampler** (val Macro F1 = 0.7019).

## Validation metrics
Best validation Macro F1: 0.7019

## Test metrics
Accuracy: 0.9384
Balanced accuracy: 0.8968
Macro precision: 0.6475
Macro recall: 0.8370
Macro F1: 0.6900
Weighted F1: 0.9492
Expected Calibration Error: 0.0070 (no explicit calibration applied)

## Limitations
- Group/record-level separation between train/val/test was NOT verified — see outputs/eda/leakage_analysis.txt.
- Trained on a single dataset; generalization to ECG images from other
  sources, scanners, or paper formats is not verified.
- Softmax confidence is not a calibrated clinical probability.
- Grad-CAM shows influential image regions only — it does not constitute a
  clinical finding.

## Intended use
Research and decision-support prototyping for the CardioSense AI image
analysis module.

## Non-intended use
Not intended as a standalone diagnostic device. Not validated for clinical
deployment. Must not replace evaluation by a qualified healthcare professional.

## Ethical considerations
CardioSense AI provides AI-generated ECG image analysis for research and
decision-support purposes. It is not a medical diagnosis and does not
replace evaluation by a qualified healthcare professional.
