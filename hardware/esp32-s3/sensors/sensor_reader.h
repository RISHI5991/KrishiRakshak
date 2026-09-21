#ifndef SENSOR_READER_H
#define SENSOR_READER_H

#include <DHT.h>
#include "../firmware/config.h"

struct DHTData {
    float temperature;
    float humidity;
    bool valid;
};

struct RainData {
    int analogValue;
    bool isRaining;
};

struct AllSensorData {
    DHTData dht;
    float soilMoisturePercent;
    int ldrRaw;
    float ldrLuxApprox;
    RainData rain;
};

class SensorReader {
private:
    DHT dht;

public:
    SensorReader() : dht(DHT_PIN, DHT_TYPE) {}

    void init() {
        dht.begin();
        pinMode(SOIL_MOISTURE_PIN, INPUT);
        pinMode(LDR_PIN, INPUT);
        pinMode(RAIN_ANALOG_PIN, INPUT);
        pinMode(RAIN_DIGITAL_PIN, INPUT);
    }

    DHTData readDHT22() {
        DHTData data;
        data.temperature = dht.readTemperature();
        data.humidity = dht.readHumidity();
        data.valid = !(isnan(data.temperature) || isnan(data.humidity));
        return data;
    }

    float readSoilMoisture() {
        int raw = analogRead(SOIL_MOISTURE_PIN);
        float pct = map(raw, DRY_VALUE, WET_VALUE, 0, 100);
        if (pct < 0) pct = 0;
        if (pct > 100) pct = 100;
        return pct;
    }

    struct LDRData {
        int raw;
        float luxApprox;
    };

    LDRData readLDR() {
        LDRData data;
        data.raw = analogRead(LDR_PIN);
        // Extremely crude approximation for 12-bit ADC
        data.luxApprox = (float)data.raw * 0.1f; 
        return data;
    }

    RainData readRainSensor() {
        RainData data;
        data.analogValue = analogRead(RAIN_ANALOG_PIN);
        data.isRaining = (digitalRead(RAIN_DIGITAL_PIN) == LOW);
        return data;
    }

    AllSensorData readAll() {
        AllSensorData data;
        data.dht = readDHT22();
        data.soilMoisturePercent = readSoilMoisture();
        LDRData ldr = readLDR();
        data.ldrRaw = ldr.raw;
        data.ldrLuxApprox = ldr.luxApprox;
        data.rain = readRainSensor();
        return data;
    }
};

#endif
