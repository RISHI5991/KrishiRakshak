# Flask API Contract

This document defines the contract between the edge devices (ESP32) and the Flask API server.

## General Principles
*   All data payloads are JSON unless otherwise specified (e.g., image uploads).
*   Standard HTTP status codes are used (200 OK, 400 Bad Request, 500 Internal Error).
*   All timestamps should be ISO 8601 strings if provided, otherwise the server will attach its own timestamp.

## Authentication
Currently, the API relies on local network security. Future iterations may include a simple Bearer token in the `Authorization` header.

## Primary Interactions

### 1. Telemetry Upload (ESP32-S3 -> Flask)
The S3 periodically sends sensor data to the server for logging and dashboard visualization.

*   **Endpoint:** `/api/telemetry`
*   **Method:** `POST`
*   **Body:** JSON object containing sensor readings.

### 2. Image Inference Request (ESP32-CAM -> Flask)
The CAM sends images for analysis.

*   **Endpoint:** `/api/analyze`
*   **Method:** `POST`
*   **Body:** `multipart/form-data` with `image` key.
*   **Response:** Combined predictions from M1-M4.

### 3. Server-Side Irrigation Decision (Optional/Override)
While the S3 can use M5 locally, the server provides a more complex fallback or override API.

*   **Endpoint:** `/api/irrigation`
*   **Method:** `POST`
*   **Body:** JSON (see `irrigation-request.json` schema).
*   **Response:** `{"decision": 1|0, "action": "water"|"skip"}`
