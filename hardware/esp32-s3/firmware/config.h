#ifndef CONFIG_H
#define CONFIG_H

#define WIFI_SSID "YOUR_SSID"
#define WIFI_PASSWORD "YOUR_PASSWORD"

#define SERVER_IP "192.168.1.100"
#define SERVER_PORT 5003

// Sensor Pins
#define DHT_PIN 4
#define DHT_TYPE DHT22
#define SOIL_MOISTURE_PIN 7
#define LDR_PIN 6
#define RAIN_ANALOG_PIN 5
#define RAIN_DIGITAL_PIN 15

// UART to WROOM
#define WROOM_UART_TX 17
#define WROOM_UART_RX 18
#define WROOM_BAUD 115200

// UART to CAM
#define CAM_UART_TX 43
#define CAM_UART_RX 44
#define CAM_BAUD 115200

// Timings
#define SENSOR_INTERVAL 5000
#define IRRIGATION_PUMP_MS 10000

// Calibration
#define DRY_VALUE 3500
#define WET_VALUE 1500

#endif
