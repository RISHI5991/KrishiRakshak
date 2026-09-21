# Pinout Reference

Complete pin allocation table for the three microcontrollers.

## ESP32-S3 N16R8 (Central)

| GPIO | Function | Subsystem |
| :--- | :--- | :--- |
| 4 | DHT22 Data | Sensors |
| 5 | Soil Moisture A0 | Sensors |
| 6 | LDR A0 | Sensors |
| 7 | Rain Sensor A0 | Sensors |
| 17 | TX to WROOM | Comm (UART1) |
| 18 | RX from WROOM | Comm (UART1) |
| 19 | TX to CAM | Comm (UART2) |
| 20 | RX from CAM | Comm (UART2) |

## ESP32-WROOM (Actuation)

| GPIO | Function | Subsystem |
| :--- | :--- | :--- |
| 16 | RX from S3 | Comm (UART2) |
| 17 | TX to S3 | Comm (UART2) |
| 13 | L298N ENA | Motors |
| 12 | L298N IN1 | Motors |
| 14 | L298N IN2 | Motors |
| 27 | L298N ENB | Motors |
| 26 | L298N IN3 | Motors |
| 25 | L298N IN4 | Motors |
| 2 | Relay IN | Pump Control |

## ESP32-CAM (Vision)

| GPIO | Function | Subsystem |
| :--- | :--- | :--- |
| 3 | RX from S3 | Comm (UART0) |
| 1 | TX to S3 | Comm (UART0) |
| *Various* | Internal Camera | Vision |
*Note: ESP32-CAM uses most of its GPIOs internally for the camera and SD card. UART0 is used for communication here, meaning standard serial debugging via USB must be disabled or carefully managed.*
