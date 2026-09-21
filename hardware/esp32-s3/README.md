# ESP32-S3 Central Coordinator

## Setup
Board: **ESP32S3 Dev Module**

## Dependencies
- ArduinoJson v7
- DHT sensor library by Adafruit

## Wiring
| Sensor | ESP32-S3 Pin |
|--------|--------------|
| DHT22  | 4            |
| Soil   | 7 (Analog)   |
| LDR    | 6 (Analog)   |
| Rain A | 5 (Analog)   |
| Rain D | 15 (Digital) |
| W-TX   | 17           |
| W-RX   | 18           |
| C-TX   | 43           |
| C-RX   | 44           |

## Calibration
Adjust `DRY_VALUE` and `WET_VALUE` in `firmware/config.h` based on dry soil and water immersion tests for the capacitive soil moisture sensor.
