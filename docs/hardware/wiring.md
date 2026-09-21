# Wiring Guide

This document outlines the physical connections between components. **Ensure power is disconnected before making changes.**

## ESP32-S3 Sensor Connections

| Component | ESP32-S3 Pin | Notes |
| :--- | :--- | :--- |
| DHT22 Data | GPIO 4 | Requires 10k pull-up resistor to 3.3V |
| DHT22 VCC | 3.3V | |
| DHT22 GND | GND | |
| Soil Moisture A0 | GPIO 5 (ADC1) | Capacitive sensor v2.0 |
| Soil Moisture VCC| 3.3V | |
| Soil Moisture GND| GND | |
| LDR A0 | GPIO 6 (ADC1) | Use voltage divider with 10k resistor |
| Rain Sensor A0 | GPIO 7 (ADC1) | |

## UART Interconnects

### ESP32-S3 ↔ ESP32-WROOM

| ESP32-S3 | ESP32-WROOM | Function |
| :--- | :--- | :--- |
| GPIO 17 (TX1) | GPIO 16 (RX2) | S3 sending commands to WROOM |
| GPIO 18 (RX1) | GPIO 17 (TX2) | S3 receiving status from WROOM |
| GND | GND | Common ground (CRITICAL) |

### ESP32-S3 ↔ ESP32-CAM

| ESP32-S3 | ESP32-CAM | Function |
| :--- | :--- | :--- |
| GPIO 19 (TX2) | GPIO 3 (RX0) | S3 sending commands to CAM |
| GPIO 20 (RX2) | GPIO 1 (TX0) | S3 receiving status from CAM |
| GND | GND | Common ground (CRITICAL) |

## ESP32-WROOM Actuator Connections

### L298N Motor Driver

| ESP32-WROOM | L298N Pin | Function |
| :--- | :--- | :--- |
| GPIO 13 | ENA | PWM speed control (Motors A) |
| GPIO 12 | IN1 | Direction control 1 |
| GPIO 14 | IN2 | Direction control 2 |
| GPIO 27 | ENB | PWM speed control (Motors B) |
| GPIO 26 | IN3 | Direction control 3 |
| GPIO 25 | IN4 | Direction control 4 |

### Relay (Water Pump)

| ESP32-WROOM | Relay Pin | Function |
| :--- | :--- | :--- |
| GPIO 2 | IN | Control signal (High = ON) |
| 5V / 3.3V | VCC | Depends on relay module specs |
| GND | GND | |

## Motor Connections to L298N

*   **OUT1 & OUT2:** Connect to left side BO motors (wired in parallel if using 4WD).
*   **OUT3 & OUT4:** Connect to right side BO motors (wired in parallel if using 4WD).
*   **12V Input:** From main battery.
*   **GND:** Common system ground.

## Power Supply Distribution

1.  **Main Battery (12V):** Connects to L298N 12V input and Buck Converter 1.
2.  **Buck Converter 1 (12V to 5V):** Powers ESP32-S3 (via VIN/5V pin), ESP32-WROOM (via VIN/5V pin), and ESP32-CAM (via 5V pin).
3.  **Buck Converter 2 (Optional, 12V to Pump Voltage):** Dedicated power for the water pump if it requires a different voltage, routed through the relay.
