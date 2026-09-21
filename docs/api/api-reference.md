# API Reference

The Dhurandhar Flask API serves as the central hub for model inference and telemetry processing. Base URL: `http://<server-ip>:<port>`

## Endpoints

### 1. Health Check
*   **URL:** `/api/health`
*   **Method:** `GET`
*   **Description:** Checks if the API is running.
*   **Success Response:**
    *   **Code:** 200 OK
    *   **Content:** `{"status": "ok", "message": "Dhurandhar API is running"}`

### 2. List Models
*   **URL:** `/api/models`
*   **Method:** `GET`
*   **Description:** Lists currently loaded models.
*   **Success Response:**
    *   **Code:** 200 OK
    *   **Content:** `{"models": ["M1", "M2", "M3", "M4", "M5"]}`

### 3. Get Classes
*   **URL:** `/api/classes/<model_id>`
*   **Method:** `GET`
*   **Description:** Returns the class labels for a specific model (e.g., M1, M2).
*   **Success Response (for M1):**
    *   **Code:** 200 OK
    *   **Content:** `{"model": "M1", "classes": ["Apple", "Corn", "Grape", ...]}`

### 4. Predict
*   **URL:** `/api/predict/<model_id>`
*   **Method:** `POST`
*   **Description:** Runs inference on a single image using the specified model.
*   **Content-Type:** `multipart/form-data`
*   **Payload:**
    *   `image`: The image file.
*   **Example cURL:**
    ```bash
    curl -X POST -F "image=@leaf.jpg" http://localhost:5000/api/predict/M1
    ```
*   **Success Response:**
    *   **Code:** 200 OK
    *   **Content:** `{"model": "M1", "prediction": "Tomato", "confidence": 0.98}`

### 5. Analyze (Full Pipeline)
*   **URL:** `/api/analyze`
*   **Method:** `POST`
*   **Description:** Runs the image through the full vision pipeline (M1, M2, M3, M4).
*   **Content-Type:** `multipart/form-data`
*   **Payload:**
    *   `image`: The image file.
*   **Success Response Schema:** See `shared/json-schemas/analyze-response.json`

### 6. Irrigation Decision
*   **URL:** `/api/irrigation`
*   **Method:** `POST`
*   **Description:** Evaluates sensor data using M5 to make an irrigation decision.
*   **Content-Type:** `application/json`
*   **Payload Schema:** See `shared/json-schemas/irrigation-request.json`
*   **Example Payload:**
    ```json
    {
      "soil_moisture_previous": 2800,
      "soil_moisture": 3100,
      "soil_moisture_trend": -300,
      "temperature": 32.5,
      "humidity": 45.0,
      "rain_recent": 0,
      "vpd": 1.5
    }
    ```
*   **Example cURL:**
    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{"soil_moisture": 3100, "temperature": 32.5, "humidity": 45.0, "soil_moisture_previous": 2800, "soil_moisture_trend": -300, "rain_recent": 0, "vpd": 1.5}' http://localhost:5000/api/irrigation
    ```
*   **Success Response:**
    *   **Code:** 200 OK
    *   **Content:** `{"decision": 1, "action": "water", "confidence": 0.85}`
