# M3 Architecture Contract

## Input

`B x 3 x 640 x 640`, ImageNet-normalized RGB.

## Backbone

`timm` MobileNetV4-ConvSmall (`mobilenetv4_conv_small.e2400_r224_in1k`), pretrained on ImageNet-1k, used with `features_only=True`.

At 640x640 in the validated user environment, the exposed features were:

- P2: `B x 32 x 160 x 160`
- P3: `B x 64 x 80 x 80`
- P4: `B x 96 x 40 x 40`

P5 is intentionally not passed through the detector neck in the first M3 release.

## Neck

A lightweight bidirectional P2/P3/P4 fusion block inspired by PicoDet/CSP-PAN design principles. Lateral projections produce:

- F2: 48 channels at stride 4
- F3: 96 channels at stride 8
- F4: 128 channels at stride 16

The downsampling path uses depthwise + pointwise convolutions.

## Head

An independent DFL-free, end-to-end-inspired head:

- direct 4-value LTRB regression (`reg_max=1` concept)
- per-class sigmoid scores
- shared separable towers
- separate one-to-many and one-to-one final prediction layers
- one-to-one path receives detached neck features during training
- inference uses the one-to-one branch

## Assignment

For each GT object, candidates are first restricted by feature level and a centre-sampling window. Only the small candidate set is scored by prediction-quality alignment. This avoids the previous all-33,600-location IoU matrix.

The first release uses a task-alignment-inspired score:

`score = class_probability^0.5 * IoU^2`

with top-k positives for one-to-many training and top-1 for one-to-one training.

## Loss

The detector uses:

- IoU + normalized SmoothL1 LTRB regression
- quality-weighted focal BCE classification
- separate one-to-many and one-to-one supervision

This is an independent M3 loss; it is not presented as a byte-for-byte reproduction of the Ultralytics YOLO26 training implementation.

## Deployment constraint

The architecture is designed around the ESP32-S3 target, but deployment feasibility is not inferred from parameter count alone. Final acceptance requires actual export, INT8 quantization, peak activation-memory measurement, operator compatibility and on-device latency testing.
