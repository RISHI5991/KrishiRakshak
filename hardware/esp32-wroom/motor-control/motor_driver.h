#ifndef MOTOR_DRIVER_H
#define MOTOR_DRIVER_H

#include "../firmware/config.h"

class MotorDriver {
public:
    void init() {
        pinMode(IN1_PIN, OUTPUT);
        pinMode(IN2_PIN, OUTPUT);
        pinMode(IN3_PIN, OUTPUT);
        pinMode(IN4_PIN, OUTPUT);
        
        // ledc setup
        ledcSetup(0, PWM_FREQ, PWM_RESOLUTION);
        ledcSetup(1, PWM_FREQ, PWM_RESOLUTION);
        
        ledcAttachPin(ENA_PIN, 0);
        ledcAttachPin(ENB_PIN, 1);
        
        stop();
    }

    void setSpeed(uint8_t leftSpeed, uint8_t rightSpeed) {
        ledcWrite(0, leftSpeed);
        ledcWrite(1, rightSpeed);
    }

    void moveForward(uint8_t speed = DEFAULT_SPEED) {
        digitalWrite(IN1_PIN, HIGH);
        digitalWrite(IN2_PIN, LOW);
        digitalWrite(IN3_PIN, HIGH);
        digitalWrite(IN4_PIN, LOW);
        setSpeed(speed, speed);
    }

    void moveBackward(uint8_t speed = DEFAULT_SPEED) {
        digitalWrite(IN1_PIN, LOW);
        digitalWrite(IN2_PIN, HIGH);
        digitalWrite(IN3_PIN, LOW);
        digitalWrite(IN4_PIN, HIGH);
        setSpeed(speed, speed);
    }

    void turnLeft(uint8_t speed = DEFAULT_SPEED) {
        digitalWrite(IN1_PIN, LOW);
        digitalWrite(IN2_PIN, HIGH);
        digitalWrite(IN3_PIN, HIGH);
        digitalWrite(IN4_PIN, LOW);
        setSpeed(speed, speed);
    }

    void turnRight(uint8_t speed = DEFAULT_SPEED) {
        digitalWrite(IN1_PIN, HIGH);
        digitalWrite(IN2_PIN, LOW);
        digitalWrite(IN3_PIN, LOW);
        digitalWrite(IN4_PIN, HIGH);
        setSpeed(speed, speed);
    }

    void stop() {
        digitalWrite(IN1_PIN, LOW);
        digitalWrite(IN2_PIN, LOW);
        digitalWrite(IN3_PIN, LOW);
        digitalWrite(IN4_PIN, LOW);
        setSpeed(0, 0);
    }
};

#endif
