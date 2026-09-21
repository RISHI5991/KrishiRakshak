# Dhurandhar M3 Pest Detector

M3 is an independently implemented edge-oriented detector for the audited Pest24 dataset.

## Architecture

MobileNetV4-ConvSmall backbone → P2/P3/P4 → lightweight bidirectional Pico/CSPPAN-inspired neck → DFL-free, end-to-end-inspired dual detection head.

The pretrained MobileNetV4 feature extractor is used through `timm`. The public model card documents `features_only=True`, ImageNet normalization, 3.8M parameters, and Apache-2.0 licensing for the published timm checkpoint. https://huggingface.co/timm/mobilenetv4_conv_small.e2400_r224_in1k

YOLO26 is used as a design reference rather than copied as an opaque training stack. Current upstream YOLO26 documents DFL-free regression (`reg_max=1`), one-to-one end-to-end inference, STAL, Progressive Loss, and MuSGD. https://docs.ultralytics.com/models/yolo26

PicoDet is used as a design reference for lightweight CSP-PAN-style multi-scale fusion and mobile-oriented deployment. https://github.com/PaddlePaddle/PaddleDetection/tree/release/2.9/configs/picodet

## Dataset assumption

This code expects the audited Pest24 directory already present at:

`datasets/Pest24/VOCdevkit/voc2007/`

and the existing manifests under `pest_ml/manifests/`.

The dataset is not included in this source archive.

## Training

From the Dhurandhar root:

```bash
python -m py_compile pest_ml/src/*.py pest_ml/scripts/*.py
python pest_ml/scripts/smoke_m3_final.py
python pest_ml/scripts/train_m3.py --epochs 30 --batch-size 2 --image-size 640
```

The default training script saves:

- `pest_ml/checkpoints/m3_pest24_last.pt`
- `pest_ml/checkpoints/m3_pest24_best.pt`
- `pest_ml/results/training_history.json`

Best-model selection is based on validation mAP50:95 when validation metrics are evaluated.

## Evaluation

```bash
python pest_ml/scripts/evaluate_m3.py --checkpoint pest_ml/checkpoints/m3_pest24_best.pt --split test --batch-size 2
```

Metrics include precision, recall, mAP50, mAP50:95 and area-aware AP for small/medium/large objects.

## Profiling

```bash
python pest_ml/scripts/profile_m3.py --image-size 640 --batch-size 1
```

## Important deployment note

The `.pt` checkpoint is a training artifact, not an ESP32-S3 runtime model. Export, integer quantization, operator compatibility, peak activation memory and actual ESP32-S3 inference latency must be validated separately before deployment.
