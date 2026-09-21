# UART Communication Protocol

This document defines the serial communication protocol between the ESP32-S3 (Master) and ESP32-WROOM (Slave).

## Transport

*   **Baud Rate:** 115200
*   **Format:** 8-N-1 (8 data bits, no parity, 1 stop bit)
*   **Encoding:** UTF-8 String containing JSON.
*   **Termination:** Newline character `\n` indicates end of message.

## Message Format

All messages must be valid JSON objects.

### 1. Commands (S3 -> WROOM)

Commands dictate actions for the WROOM to perform.

**Schema:**
```json
{
  "cmd": "<command_name>",
  "args": {
    // Command specific arguments
  }
}
```

**Supported Commands:**

*   **`move`**: Control motors.
    *   `args`: `{"dir": "fwd"|"rev"|"left"|"right"|"stop", "speed": 0-255}`
*   **`pump`**: Control water pump.
    *   `args`: `{"state": "on"|"off", "duration_ms": <integer>}` (duration optional, turns off automatically if provided)

### 2. Responses (WROOM -> S3)

Responses acknowledge commands or report status.

**Schema:**
```json
{
  "status": "ack" | "error" | "info",
  "msg": "<optional text>",
  "data": {
    // Optional data
  }
}
```

## Example Interaction

**S3 sends command to move forward:**
`{"cmd": "move", "args": {"dir": "fwd", "speed": 150}}\n`

**WROOM replies:**
`{"status": "ack", "msg": "moving fwd"}\n`

**S3 sends command to water for 5 seconds:**
`{"cmd": "pump", "args": {"state": "on", "duration_ms": 5000}}\n`

**WROOM replies (immediately):**
`{"status": "ack", "msg": "pump on timer started"}\n`

**WROOM replies (after 5 seconds):**
`{"status": "info", "msg": "pump timer finished"}\n`
