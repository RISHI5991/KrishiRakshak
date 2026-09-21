# ESP32-CAM Firmware

## Prerequisites
- AI-Thinker ESP32-CAM module
- FTDI Programmer (USB to TTL serial converter)
- 5V power supply (ESP32-CAM requires a stable 5V)

## Arduino IDE Setup
1. Open Arduino IDE
2. Go to Preferences -> Additional Boards Manager URLs and add `https://dl.espressif.com/dl/package_esp32_index.json`
3. Go to Tools -> Board -> Boards Manager, search for `esp32` and install.
4. Select Board: **AI Thinker ESP32-CAM**
5. Dependencies: `WiFi`, `HTTPClient` (built-in).

## Configuration
Update `firmware/config.h` with your WiFi credentials and Flask server details.

## Flashing Instructions
1. Connect FTDI to ESP32-CAM:
   - 5V -> 5V
   - GND -> GND
   - TX -> U0R
   - RX -> U0T
2. Short **GPIO0 to GND** to enter flash mode.
3. Press the RST button on the ESP32-CAM.
4. Click Upload in Arduino IDE.
5. Once done, disconnect GPIO0 from GND and press RST again.
