#include <ArduinoJson.h>
#include <WiFi.h>
#include <HTTPClient.h>

#include "config.h"
#include "../sensors/sensor_reader.h"
#include "../sensors/vpd_calculator.h"

SensorReader sensors;

float prevSoilMoisture = 0.0;

void connectWiFi() {
    Serial.print("Connecting to WiFi...");
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi connected.");
}

void setup() {
    Serial.begin(115200);
    
    // UART to WROOM
    Serial1.begin(WROOM_BAUD, SERIAL_8N1, WROOM_UART_RX, WROOM_UART_TX);
    
    // UART to CAM
    Serial2.begin(CAM_BAUD, SERIAL_8N1, CAM_UART_RX, CAM_UART_TX);
    
    sensors.init();
    connectWiFi();
    
    Serial.println("S3 Coordinator Init Complete.");
}

void sendToWroom(String jsonCmd) {
    Serial1.println(jsonCmd);
}

void receiveFromWroom() {
    while (Serial1.available()) {
        String resp = Serial1.readStringUntil('\n');
        Serial.println("WROOM: " + resp);
    }
}

void loop() {
    if (WiFi.status() != WL_CONNECTED) {
        connectWiFi();
    }

    AllSensorData data = sensors.readAll();
    float vpd = calculateVPD(data.dht.temperature, data.dht.humidity);
    float soilMoistureTrend = data.soilMoisturePercent - prevSoilMoisture;
    prevSoilMoisture = data.soilMoisturePercent;

    // Build JSON payload
    JsonDocument doc;
    doc["temperature"] = data.dht.temperature;
    doc["humidity"] = data.dht.humidity;
    doc["soil_moisture"] = data.soilMoisturePercent;
    doc["soil_moisture_trend"] = soilMoistureTrend;
    doc["light_lux"] = data.ldrLuxApprox;
    doc["is_raining"] = data.rain.isRaining;
    doc["vpd"] = vpd;

    String jsonPayload;
    serializeJson(doc, jsonPayload);
    
    Serial.println("Sending: " + jsonPayload);

    // HTTP POST
    HTTPClient http;
    String url = "http://" + String(SERVER_IP) + ":" + String(SERVER_PORT) + "/api/irrigation";
    http.begin(url);
    http.addHeader("Content-Type", "application/json");
    
    int httpResponseCode = http.POST(jsonPayload);
    
    if (httpResponseCode > 0) {
        String response = http.getString();
        Serial.println("Server Response: " + response);
        
        JsonDocument respDoc;
        DeserializationError error = deserializeJson(respDoc, response);
        if (!error) {
            String decision = respDoc["decision"] | "";
            if (decision == "IRRIGATE") {
                JsonDocument cmdDoc;
                cmdDoc["cmd"] = "PO";
                cmdDoc["dur"] = IRRIGATION_PUMP_MS;
                String cmdStr;
                serializeJson(cmdDoc, cmdStr);
                sendToWroom(cmdStr);
            }
        }
    } else {
        Serial.println("HTTP Error: " + String(httpResponseCode));
    }
    http.end();

    receiveFromWroom();

    delay(SENSOR_INTERVAL);
}
