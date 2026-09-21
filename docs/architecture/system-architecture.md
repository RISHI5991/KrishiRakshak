# System Architecture

The Dhurandhar agricultural robotics project utilizes a distributed computing architecture spanning edge devices, local servers, and cloud interfaces. This document outlines the holistic system design.

## 3-ESP32 Hardware Topology

The robot's edge intelligence and control are distributed across three ESP32 microcontrollers to ensure modularity and reliability.

```mermaid
graph TD
    subgraph Edge Hardware
        CAM[ESP32-CAM: Vision Node]
        S3[ESP32-S3 N16R8: Central Coordinator]
        WROOM[ESP32-WROOM: Actuation Node]
        
        CAM -- UART --> S3
        S3 -- UART --> WROOM
    end
    
    subgraph Actuators & Sensors
        S3 --> DHT22
        S3 --> SoilMoisture[Soil Moisture v2.0]
        S3 --> LDR
        S3 --> RainSensor
        
        WROOM --> L298N[L298N Motor Driver]
        L298N --> Motors[4x BO Motors]
        WROOM --> Relay
        Relay --> Pump[Water Pump]
    end
```

## Software Stack Layers

The software architecture is divided into distinct layers:

1.  **Hardware Abstraction Layer (HAL):** Firmware running on the ESP32s (C++).
2.  **Communication Layer:** UART for intra-robot communication; WiFi (HTTP/REST) for robot-to-server.
3.  **Inference Service Layer:** Flask API gateway handling requests and orchestrating ML model inference.
4.  **Application Layer:** Android app (Jetpack Compose) and Web dashboard for user interaction.

## Communication Paths

```mermaid
flowchart LR
    ESP32_S3 <-->|WiFi / REST| Flask_API
    ESP32_CAM -->|WiFi / REST| Flask_API
    Flask_API <-->|REST| Web_Dashboard
    Flask_API <-->|REST| Android_App
```

## AI Pipeline Flow

The AI pipeline is triggered by incoming telemetry or images.

```mermaid
sequenceDiagram
    participant Hardware as ESP32 (S3/CAM)
    participant Flask as Flask API
    participant M1 as Crop Classifier
    participant M2 as Disease Classifier
    participant M5 as Irrigation Model
    
    Hardware->>Flask: POST /api/predict (Image)
    Flask->>M1: Inference
    M1-->>Flask: Crop Type
    Flask->>M2: Inference
    M2-->>Flask: Disease State
    Flask-->>Hardware: Analysis Results
    
    Hardware->>Flask: POST /api/irrigation (Sensors)
    Flask->>M5: Evaluate conditions
    M5-->>Flask: Irrigation Decision
    Flask-->>Hardware: Pump Command
```

## Design Decisions and Trade-offs

*   **Multi-MCU Design:** Using 3 ESP32s prevents blocking operations. The camera node doesn't halt motor control during image capture. Trade-off: increased complexity in UART communication and power distribution.
*   **Centralized AI vs Edge AI:** Heavy vision models run on the Flask server due to ESP32 memory constraints. Trade-off: Requires reliable WiFi connection, but allows for much more accurate, larger models (MobileNet, YOLO) than TinyML on edge.
