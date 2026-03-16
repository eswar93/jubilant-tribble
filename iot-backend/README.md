# Simple IoT backend (learning project)

This micro backend demonstrates how to control an ESP32 device from a Python FastAPI server.

Run the server:

```bash
python -m pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Endpoints:
- `POST /devices/register` - register a device (optional `device_id` in JSON)
- `POST /devices/{device_id}/telemetry` - device sends telemetry JSON
- `GET /devices/{device_id}/telemetry` - read stored telemetry
- `POST /devices/{device_id}/commands` - server (or operator) posts command JSON to device
- `GET /devices` - list registered devices
- `WS /ws/{device_id}` - device connects via WebSocket to receive commands in realtime

Quick curl examples:

Register a device:

```bash
curl -X POST "http://localhost:8000/devices/register" -H "Content-Type: application/json" -d '{"model":"esp32-demo"}'
```

Post a command to a device:

```bash
curl -X POST "http://localhost:8000/devices/<device_id>/commands" -H "Content-Type: application/json" -d '{"action":"led_on"}'
```

ESP32 example sketch is in `esp32_samples/esp32_example.ino`.
