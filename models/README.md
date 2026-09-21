# Models

This directory contains the trained model weights and exported deployment formats for the Dhurandhar project.

> [!WARNING]
> Due to GitHub file size limits, large model artifacts (`.keras`, `.pt`, `.onnx`) are **not tracked** in this repository. 

## Model Artifacts

The following files are required for the Flask API and edge deployment to function correctly.

### Main Vision Models
*   **`M1:`** `AgriGuard_Model1_Final.keras` (15 crop classes)
*   **`M2:`** `AgriGuard_Model2_Final.keras` (38 disease classes)
*   **`M3:`** `m3_pest24_best.pt` (24 pest classes, YOLO/PyTorch format)
*   **`M4:`** `npk_vision_baseline_v1.pt` (4 nutrient classes, PyTorch format)

### Edge/Tabular Models
*   **`M5:`** `m3_embedded_rf.joblib` (Irrigation Random Forest, scikit-learn format)

### TFLite Exports (for alternative edge deployment)
*   `AgriGuard_Model1_Final_fp32.tflite`
*   `AgriGuard_Model1_Final_fp16.tflite`
*   `AgriGuard_Model1_Final_int8.tflite` (Requires representative dataset for calibration)
*   `AgriGuard_Model2_Final_fp32.tflite`
*   ...and so on.

## How to Get the Models

1.  **Download:** Check the project releases page or internal shared drive for a `.zip` file containing the latest weights.
2.  **Extract:** Unzip the contents directly into this `models/` directory.
3.  **Train:** Alternatively, follow the training scripts in `scripts/train/` (if available) to train the models from scratch using the datasets described in `datasets/README.md`.
