# ESP32-WROOM Actuator Controller

## Setup
Board: **ESP32 Dev Module**

## Wiring
| Component | WROOM Pin |
|-----------|-----------|
| L298N ENA | 13        |
| L298N IN1 | 12        |
| L298N IN2 | 14        |
| L298N ENB | 27        |
| L298N IN3 | 26        |
| L298N IN4 | 25        |
| Pump Relay| 2         |
| S3 UART RX| 16        |
| S3 UART TX| 17        |

## Safety
- Use a separate 12V supply for motors.
- Connect common ground between ESP32 and L298N.
- Use a flyback diode on the pump motor.
