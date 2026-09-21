#include <ArduinoJson.h>
#include "config.h"
#include "../motor-control/motor_driver.h"
#include "../pump-control/pump_controller.h"

MotorDriver motors;
PumpController pump;

unsigned long lastCmdTime = 0;

void setup() {
    Serial.begin(115200);
    Serial2.begin(S3_BAUD, SERIAL_8N1, S3_UART_RX, S3_UART_TX);
    
    motors.init();
    pump.init(PUMP_RELAY_PIN);
    
    lastCmdTime = millis();
    Serial.println("WROOM Actuator Init Complete.");
}

void sendAck(const char* cmd, bool ok) {
    JsonDocument doc;
    doc["ack"] = ok ? "OK" : "NK";
    doc["cmd"] = cmd;
    
    String response;
    serializeJson(doc, response);
    Serial2.println(response);
}

void processCommand(String jsonStr) {
    JsonDocument doc;
    DeserializationError error = deserializeJson(doc, jsonStr);
    
    if (error) {
        sendAck("UNKNOWN", false);
        return;
    }

    String cmd = doc["cmd"] | "";
    uint8_t spd = doc["spd"] | DEFAULT_SPEED;
    unsigned long dur = doc["dur"] | 0;

    bool valid = true;

    if (cmd == "MF") { motors.moveForward(spd); }
    else if (cmd == "MB") { motors.moveBackward(spd); }
    else if (cmd == "TL") { motors.turnLeft(spd); }
    else if (cmd == "TR") { motors.turnRight(spd); }
    else if (cmd == "ST") { motors.stop(); }
    else if (cmd == "PO") { pump.turnOn(dur); }
    else if (cmd == "PF") { pump.turnOff(); }
    else if (cmd == "SR") { /* Just status */ }
    else { valid = false; }

    if (valid) {
        lastCmdTime = millis();
    }
    
    sendAck(cmd.c_str(), valid);
}

void loop() {
    if (Serial2.available()) {
        String jsonStr = Serial2.readStringUntil('\n');
        processCommand(jsonStr);
    }
    
    pump.update();
    
    if (millis() - lastCmdTime > WATCHDOG_TIMEOUT_MS) {
        motors.stop();
        lastCmdTime = millis(); // Reset to avoid constant triggering
    }
}
