from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import asyncio
import uuid

app = FastAPI(title="Simple IoT Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory stores (for learning/demo only)
devices: Dict[str, Dict[str, Any]] = {}
command_queues: Dict[str, asyncio.Queue] = {}


@app.get("/")
def read_root():
    return {"message": "IoT backend running"}


@app.post("/devices/register")
async def register_device(payload: Dict[str, Any]):
    """Register a device. Provide optional `device_id`; server will create one if missing."""
    device_id = payload.get("device_id") or str(uuid.uuid4())
    devices[device_id] = {**payload, "device_id": device_id}
    if device_id not in command_queues:
        command_queues[device_id] = asyncio.Queue()
    return {"device_id": device_id}


@app.get("/devices")
def list_devices():
    return {"devices": list(devices.keys())}


@app.post("/devices/{device_id}/telemetry")
async def ingest_telemetry(device_id: str, payload: Dict[str, Any]):
    """Devices POST telemetry here."""
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="device not registered")
    devices[device_id].setdefault("telemetry", []).append(payload)
    return {"status": "ok"}


@app.get("/devices/{device_id}/telemetry")
def get_telemetry(device_id: str):
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="device not registered")
    return {"telemetry": devices[device_id].get("telemetry", [])}


@app.post("/devices/{device_id}/commands")
async def post_command(device_id: str, payload: Dict[str, Any]):
    """Create a command to be delivered to the device. Commands are queued and sent over WebSocket."""
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="device not registered")
    cmd_id = str(uuid.uuid4())
    command = {"id": cmd_id, "command": payload}
    await command_queues[device_id].put(command)
    return {"command_id": cmd_id}


@app.websocket("/ws/{device_id}")
async def device_ws(websocket: WebSocket, device_id: str):
    """WebSocket endpoint that a device connects to in order to receive commands in realtime.
    The device should open this socket and wait for incoming JSON commands.
    """
    await websocket.accept()
    # ensure device exists and has a queue
    if device_id not in devices:
        devices[device_id] = {"device_id": device_id}
    if device_id not in command_queues:
        command_queues[device_id] = asyncio.Queue()

    queue: asyncio.Queue = command_queues[device_id]
    try:
        while True:
            # Wait for next command and send it
            command = await queue.get()
            await websocket.send_json(command)
    except WebSocketDisconnect:
        return