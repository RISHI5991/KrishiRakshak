# Dhurandhar UART Protocol

## Message Format
- Newline-delimited JSON payload.
- Baud Rate: 115200

## Commands
| Command | Action | Example |
|---------|--------|---------|
| MF | Move Forward | `{"cmd":"MF","spd":200}` |
| MB | Move Backward | `{"cmd":"MB","spd":200}` |
| TL | Turn Left | `{"cmd":"TL","spd":180}` |
| TR | Turn Right | `{"cmd":"TR","spd":180}` |
| ST | Stop Motors | `{"cmd":"ST"}` |
| PO | Pump On | `{"cmd":"PO","dur":10000}` |
| PF | Pump Off | `{"cmd":"PF"}` |
| SR | Status Req | `{"cmd":"SR"}` |

## Responses
The actuator sends an acknowledgment back.
Format: `{"ack":"OK","cmd":"MF"}` or `{"ack":"NK","cmd":"UNKNOWN"}`

## Error Handling
If JSON is invalid, returns `NK` with command `UNKNOWN`.

## Timing
Motors automatically stop if no command is received within the watchdog timeout (5000ms).
