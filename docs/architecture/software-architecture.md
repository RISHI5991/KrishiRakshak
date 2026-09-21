# Software Architecture

The Dhurandhar software stack is modular, decoupling the hardware control, AI inference, and user interfaces.

## Software Components

### 1. Flask AI Gateway (Inference Service)
*   **Role:** Central server routing requests from the robot and UI to the ML models.
*   **Tech:** Python, Flask, PyTorch, scikit-learn.
*   **Functionality:** Exposes REST endpoints for model inference, aggregates data, and logs system state.

### 2. Android App
*   **Role:** Mobile interface for farmers.
*   **Tech:** Kotlin, Jetpack Compose, Material 3 design system.
*   **Functionality:** Displays real-time dashboards, manual override controls, and historical crop health data.

### 3. Web Dashboard
*   **Role:** Desktop monitoring interface.
*   **Tech:** Vanilla HTML/CSS/JS (no heavy frameworks for simplicity).
*   **Functionality:** Real-time telemetry visualization, log viewing, and remote configuration.

### 4. Inference Pipeline
Located within the Flask API, the inference code is modularized:
*   `classifier.py`: Wraps M1 (Crop) and M2 (Disease) models. Handles image preprocessing and tensor management.
*   `pest.py`: Wraps the M3 (YOLO/MCUNet) object detection model. Formats bounding box outputs.
*   `irrigation.py`: Wraps the M5 (RandomForest) tabular model.

### 5. Model Registry Pattern
Models are loaded via a central registry in the Flask app. This ensures models are loaded into memory only once at startup (singleton pattern) and can be easily swapped or versioned by changing the configuration, without altering the route handlers.
