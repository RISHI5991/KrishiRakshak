# Dhurandhar Edge ML V1

Locked accuracy model:
- MobileNetV4-ConvSmall
- shared backbone
- 256x256 RGB input
- M1: 15 classes
- M2: 38 crop-condition classes

The training recipe intentionally follows the useful parts of the existing AgriGuard notebook: ImageNet transfer learning, class-balanced weighting, strong training augmentation, dropout, adaptive learning-rate reduction, validation checkpointing and early stopping. The old SIH History is intentionally not used as an ML training reference.

## Copy files

Copy these files into `/Users/rishisharma/Dhurandhar/edge_ml/`:
- config.py
- model.py
- dataset.py
- train.py
- evaluate.py

## Run

From `/Users/rishisharma/Dhurandhar`:

```bash
source /Users/rishisharma/Dhurandhar/AgriGuard/.agriguard-venv/bin/activate
python edge_ml/train.py
```

After the baseline finishes:

```bash
python edge_ml/evaluate.py
```

This first run is deliberately supervised-only. The AgriGuard teacher-distillation cache is the next planned phase after this baseline has been verified; it does not change the architecture.
