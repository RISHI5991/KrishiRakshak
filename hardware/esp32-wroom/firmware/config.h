#ifndef CONFIG_H
#define CONFIG_H

// L298N pins
#define ENA_PIN 13
#define IN1_PIN 12
#define IN2_PIN 14
#define ENB_PIN 27
#define IN3_PIN 26
#define IN4_PIN 25

// Pump relay
#define PUMP_RELAY_PIN 2

// UART from S3 (UART2)
#define S3_UART_RX 16
#define S3_UART_TX 17
#define S3_BAUD 115200

#define PUMP_MAX_MS 30000
#define WATCHDOG_TIMEOUT_MS 5000

#define PWM_FREQ 5000
#define PWM_RESOLUTION 8
#define DEFAULT_SPEED 180

#endif
