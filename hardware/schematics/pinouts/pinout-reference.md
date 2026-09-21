# Pinout Reference Map

> [!NOTE]
> This document mirrors the simplified pinout guide in `docs/hardware/pinout.md` but is kept here in the schematics folder for CAD/PCB design reference.

## Master Pin Allocation

| Subsystem | Microcontroller | Pin Name | Pin Number / GPIO | Function description |
| :--- | :--- | :--- | :--- | :--- |
| Sensors | S3 (Master) | D4 | GPIO 4 | Digital Read (DHT22) |
| Sensors | S3 (Master) | A5 | GPIO 5 | Analog Read (Soil) |
| Sensors | S3 (Master) | A6 | GPIO 6 | Analog Read (LDR) |
| Sensors | S3 (Master) | A7 | GPIO 7 | Analog Read (Rain) |
| Comm | S3 (Master) | TX1 | GPIO 17 | UART1 TX (to WROOM) |
| Comm | S3 (Master) | RX1 | GPIO 18 | UART1 RX (from WROOM) |
| Comm | S3 (Master) | TX2 | GPIO 19 | UART2 TX (to CAM) |
| Comm | S3 (Master) | RX2 | GPIO 20 | UART2 RX (from CAM) |
| Comm | WROOM (Actuator) | RX2 | GPIO 16 | UART2 RX (from S3) |
| Comm | WROOM (Actuator) | TX2 | GPIO 17 | UART2 TX (to S3) |
| Motors | WROOM (Actuator) | D13 | GPIO 13 | PWM Out (ENA) |
| Motors | WROOM (Actuator) | D12 | GPIO 12 | Digital Out (IN1) |
| Motors | WROOM (Actuator) | D14 | GPIO 14 | Digital Out (IN2) |
| Motors | WROOM (Actuator) | D27 | GPIO 27 | PWM Out (ENB) |
| Motors | WROOM (Actuator) | D26 | GPIO 26 | Digital Out (IN3) |
| Motors | WROOM (Actuator) | D25 | GPIO 25 | Digital Out (IN4) |
| Pump | WROOM (Actuator) | D2 | GPIO 2 | Digital Out (Relay IN) |
| Comm | CAM (Vision) | RX0 | GPIO 3 | UART0 RX (from S3) |
| Comm | CAM (Vision) | TX0 | GPIO 1 | UART0 TX (to S3) |
