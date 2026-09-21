# Model Benchmarks

Benchmark results for the production versions of the Dhurandhar ML models.

## Vision Models (Server-Side Inference)

| Model | Task | Parameters | Input Size | Inference Time (CPU) | Inference Time (GPU) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| M1 (Crop) | Classification | 3.2M | 224x224 | ~45ms | ~8ms |
| M2 (Disease) | Classification | 3.4M* | 224x224 | ~48ms | ~8ms |
| M3 (YOLO26n)| Detection | 4.1M | 640x640 | ~120ms | ~15ms |
| M4 (Nutrient)| Classification | 1.8M | 224x224 | ~30ms | ~5ms |
*\*Note: M2 parameter count includes the shared backbone.*

## M3 (Pest Detection) AP Metrics
*   **mAP50:** 0.82
*   **mAP50:95:** 0.61
*   **Small Object AP:** 0.45
*   **Medium Object AP:** 0.68
*   **Large Object AP:** 0.88

## M4 (Nutrient Deficiency) Metrics
*   **Overall Accuracy:** 92.5%
*   **F1-Score (Healthy):** 0.95
*   **F1-Score (N Def):** 0.91
*   **F1-Score (P Def):** 0.89
*   **F1-Score (K Def):** 0.93

## Edge Models (Microcontroller Inference)

| Model | Task | Accuracy | Model Size (Binary) | RAM Usage | Inference Time (ESP32-S3) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| M5 (RF) | Irrigation | 96.8% | ~12 KB | < 2 KB | < 1ms |
