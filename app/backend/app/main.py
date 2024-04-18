from typing import Callable
import re
import asyncio
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from sse_starlette.sse import EventSourceResponse, ServerSentEvent

import aiomqtt

from app.model.config import Settings
from app.model.sensor_manager import SensorManager


MQTT_TOPIC = "wcs/sensors/+/+"
MQTT_REGEX = "wcs/sensors/([^/]+)/([^/]+)"


sensors: SensorManager = SensorManager()
connections: set[Callable] = set()
settings = Settings()

async def listen_mqtt(settings: Settings, sensors: SensorManager, connections):
    while True:
        try:
            async with aiomqtt.Client(
                hostname=settings.mqtt_host,
                port=settings.mqtt_port,
                username=settings.mqtt_username,
                password=settings.mqtt_password,
                keepalive=settings.mqtt_keepalive,
            ) as client:
                print(f"MQTT Broker {settings.mqtt_host}:{settings.mqtt_port} connected.")

                await client.subscribe(MQTT_TOPIC)
                async for message in client.messages:
                    match = re.match(MQTT_REGEX, message.topic.value)
                    if match:
                        sensor_id = match.group(1)
                        property_name = match.group(2)
                        property_value = (
                            message.payload.decode("utf-8")
                            if isinstance(message.payload, (bytes, bytearray))
                            else message.payload
                        )

                        if sensors.update_state(sensor_id, property_name, property_value):
                            data = {"sensor": sensor_id, "state": {property_name: property_value}}
                            for func in connections:
                                await func(data)
        except aiomqtt.MqttError:
            print(f"MQTT Broker {settings.mqtt_host}:{settings.mqtt_port} connection lost.")
            print(f"Reconnecting in {settings.mqtt_reconnect_timeout} seconds...")
            await asyncio.sleep(settings.mqtt_reconnect_timeout)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Listen for MQTT messages in (unawaited) asyncio task
    global sensors, connections
    loop = asyncio.get_event_loop()
    task = loop.create_task(listen_mqtt(settings, sensors, connections))

    yield

    # Cancel the task
    task.cancel()
    # Wait for the task to be cancelled
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/sensors/list")
async def get_sensors_list() -> JSONResponse:
    response = {}
    for k, v in sensors.get_sensors().items():
        response[k] = v | {"state": sensors.get_state(k)}

    return JSONResponse(response)


@app.get("/sensors/map")
async def get_sensors_map() -> FileResponse:
    response = settings.data_map
    return FileResponse(response)


@app.get("/sse/sensors")
async def sse_sensors_stream(request: Request) -> EventSourceResponse:
    queue = asyncio.Queue()

    async def receive_notification(payload):
        # Receives updates and forwards them to the queue
        await queue.put(payload)

    async def generate_stream():
        global connections
        connections.add(receive_notification)
        print(f"Client {request.client.host}:{request.client.port} connected.")

        try:
            while True:
                payload = await queue.get()
                yield ServerSentEvent(data=json.dumps(payload), event="message")
        except asyncio.CancelledError as e:
            # when the browser disconects, cancels notifications
            connections.remove(receive_notification)
            print(f"Client {request.client.host}:{request.client.port} disconnected.")
            raise e

    return EventSourceResponse(generate_stream())
