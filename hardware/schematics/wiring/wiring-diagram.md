# Wiring Diagram Reference

This document serves as the master wiring table for the complete Dhurandhar robotic system.

## 1. Core Logic (ESP32-S3)
| Component Pin | ESP32-S3 Pin | Purpose |
| :--- | :--- | :--- |
| **DHT22** VCC | 3.3V | Power |
| **DHT22** GND | GND | Ground |
| **DHT22** DATA | GPIO 4 | Temp/Humidity Data (needs 10k pull-up) |
| **Soil v2** VCC | 3.3V | Power |
| **Soil v2** GND | GND | Ground |
| **Soil v2** AOUT | GPIO 5 (ADC1) | Analog Moisture |
| **LDR** VCC | 3.3V (via R1) | Power |
| **LDR** GND | GND (via LDR) | Ground |
| **LDR** OUT | GPIO 6 (ADC1) | Analog Light |
| **Rain** VCC | 3.3V | Power |
| **Rain** GND | GND | Ground |
| **Rain** AOUT | GPIO 7 (ADC1) | Analog Rain |

## 2. Actuation Logic (ESP32-WROOM)
| Component Pin | ESP32-WROOM Pin | Purpose |
| :--- | :--- | :--- |
| **L298N** ENA | GPIO 13 | Left Motors Speed (PWM) |
| **L298N** IN1 | GPIO 12 | Left Motors Dir A |
| **L298N** IN2 | GPIO 14 | Left Motors Dir B |
| **L298N** ENB | GPIO 27 | Right Motors Speed (PWM) |
| **L298N** IN3 | GPIO 26 | Right Motors Dir A |
| **L298N** IN4 | GPIO 25 | Right Motors Dir B |
| **Relay** VCC | 5V | Power |
| **Relay** GND | GND | Ground |
| **Relay** IN | GPIO 2 | Pump Control |

## 3. Inter-Device Bus (UART)
| TX Device/Pin | RX Device/Pin | Flow |
| :--- | :--- | :--- |
| **S3** / GPIO 17 | **WROOM** / GPIO 16 | S3 commands WROOM |
| **WROOM** / GPIO 17 | **S3** / GPIO 18 | WROOM status to S3 |
| **S3** / GPIO 19 | **CAM** / GPIO 3 | S3 commands CAM |
| **CAM** / GPIO 1 | **S3** / GPIO 20 | CAM status to S3 |
| **System GND** | **System GND** | CRITICAL: Common Ground |

## 4. Power Path
| Source | Destination | Voltage |
| :--- | :--- | :--- |
| 12V Battery | L298N (12V IN) | 12V |
| 12V Battery | Buck Converter 1 (IN) | 12V |
| Buck Conv 1 (OUT) | ESP32-S3 (VIN) | 5V |
| Buck Conv 1 (OUT) | ESP32-WROOM (VIN) | 5V |
| Buck Conv 1 (OUT) | ESP32-CAM (5V pin) | 5V |
