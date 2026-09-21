# ML Experiments

This document logs the core experiments conducted to develop the Dhurandhar AI pipeline.

## M1 (Crop) and M2 (Disease) - Shared Backbone
*   **Goal:** Classify 15 crop types and 38 disease states accurately while minimizing overall memory footprint.
*   **Architecture:** `edge_ml` strategy. We use a MobileNetV4 backbone. The feature maps are fed into two separate classification heads.
*   **Dataset:** Augmented PlantVillage (38 classes) + custom crop dataset (15 classes).
*   **Results:** Shared backbone reduced parameter count by ~40% compared to two independent MobileNetV4 models, with only a 1.2% drop in validation accuracy for M2.

## M3 - Pest Detection
*   **Goal:** Detect and classify 24 pest species on leaves.
*   **Baseline:** YOLO26n. Excellent mAP but too heavy for edge deployment.
*   **Experiment 1:** M3 Hybrid (YOLO neck + lightweight backbone).
*   **Experiment 2 (Current Focus):** Student MCUNet. We are distilling the YOLO baseline into an MCUNet architecture specifically targeted for the ESP32-CAM.
*   **Dataset:** Pest24 (VOC format) merged with leaf_pest_detection (YOLO format).

## M4 - Nutrient Deficiency
*   **Goal:** Identify N, P, K deficiencies or Healthy status in rice crops.
*   **Dataset:** HARN Rice dataset (4 classes).
*   **Analysis:** Used GradCAM during validation to ensure the model focuses on leaf discoloration patterns rather than background soil.
*   **Architecture:** Custom lightweight CNN based on MobileNetV2 structure.

## M5 - Irrigation Logic
*   **Goal:** Predict whether irrigation is needed based on environmental telemetry.
*   **Architecture:** Random Forest Classifier. Chosen because it can be easily exported to pure C code via `emlearn`.
*   **Features (7):** `soil_moisture_previous`, `soil_moisture`, `soil_moisture_trend`, `temperature`, `humidity`, `rain_recent`, `vpd`.
*   **Target:** Binary (1 = Water, 0 = Don't Water).
*   **Deployment:** Exported as a C header file and compiled directly into the ESP32-S3 firmware.
