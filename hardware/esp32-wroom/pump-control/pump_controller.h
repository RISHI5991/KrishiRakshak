#ifndef PUMP_CONTROLLER_H
#define PUMP_CONTROLLER_H

#include "../firmware/config.h"

class PumpController {
private:
    uint8_t pin;
    bool running;
    unsigned long shutoffTime;

public:
    void init(uint8_t relayPin) {
        pin = relayPin;
        pinMode(pin, OUTPUT);
        turnOff();
    }

    void turnOn(unsigned long durationMs) {
        if (durationMs > PUMP_MAX_MS) {
            durationMs = PUMP_MAX_MS;
        }
        running = true;
        shutoffTime = millis() + durationMs;
        digitalWrite(pin, HIGH); // Assuming active HIGH relay
    }

    void turnOff() {
        running = false;
        digitalWrite(pin, LOW);
    }

    void update() {
        if (running && millis() > shutoffTime) {
            turnOff();
        }
    }

    bool isRunning() {
        return running;
    }
};

#endif
