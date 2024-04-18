import network
import machine
import _thread
import asyncio
from umqtt.simple import MQTTClient
import config
from lib.threadsafe import Message
from lib.led_async import AsyncLED


ONBOARD_LED_GPIO = 2
LED_FLASHING_RATE_CONNECTING_TO_WLAN = 2
LED_FLASHING_RATE_CONNECTING_TO_MQTT = 6

LIQUID_SENSOR_GPIO = 21


async def sync_to_async(func, *args, **kwargs):
    def wrap(func, message, args, kwargs):
        # Run the blocking function.
        try:
            message.set(func(*args, **kwargs))
        except Exception as e:
            message.set(e)

    msg = Message()
    _thread.start_new_thread(wrap, (func, msg, args, kwargs))
    return await msg


def initialize():
    network.hostname(config.SENSOR_HOSTNAME)


async def connect_to_wlan(ssid: str, password: str):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        # get millisecond counter
        # time_start = time.ticks_ms()

        print(f"Connecting to WLAN {ssid}...", end="")
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            print(".", end="")
            await asyncio.sleep_ms(500)
        print()

        # compute time difference
        # time_delta = time.ticks_diff(time.ticks_ms(), time_start)

    print(f"Connected to WLAN {ssid}.")
    print("{}/{}, net={}, gw={}, dns={}".format(network.hostname(), *wlan.ifconfig()))


async def connect_to_mqtt(
    client_id: str,
    host: str,
    port: int,
    user: str,
    password: str,
    keepalive: int,
    last_will_topic: bytes,
    last_will_message: bytes,
):
    mqtt: MQTTClient = MQTTClient(
        client_id, host, port=port, user=user, password=password, keepalive=keepalive
    )
    mqtt.set_last_will(last_will_topic, last_will_message, retain=True, qos=0)

    result = await sync_to_async(mqtt.connect, True)
    if isinstance(result, Exception):
        raise result

    return mqtt


def get_liquid_sensor_value(signal: machine.Signal) -> int:
    return signal.value()


async def main():
    initialize()

    onboard_led: AsyncLED = AsyncLED(machine.Signal(machine.Pin(ONBOARD_LED_GPIO, machine.Pin.OUT)))
    liquid_sensor: machine.Signal = machine.Signal(machine.Pin(LIQUID_SENSOR_GPIO, machine.Pin.IN))

    onboard_led.flash(LED_FLASHING_RATE_CONNECTING_TO_WLAN)
    await connect_to_wlan(config.WLAN_NETWORK, config.WLAN_PASSWORD)

    onboard_led.flash(LED_FLASHING_RATE_CONNECTING_TO_MQTT)
    print(f"Connecting to MQTT Broker at {config.MQTT_BROKER_HOST}...")
    mqtt: MQTTClient = await connect_to_mqtt(
        config.SENSOR_HOSTNAME,
        config.MQTT_BROKER_HOST,
        config.MQTT_BROKER_PORT,
        config.MQTT_BROKER_USER_NAME,
        config.MQTT_BROKER_USER_PASSWORD,
        config.MQTT_BROKER_KEEPALIVE,
        config.MQTT_TOPIC_ROOT + config.MQTT_TOPIC_STATUS,
        config.MQTT_TOPIC_STATUS_DOWN,
    )
    print("Connected to MQTT Broker.")

    result = await sync_to_async(
        mqtt.publish, config.MQTT_TOPIC_ROOT + config.MQTT_TOPIC_STATUS, config.MQTT_TOPIC_STATUS_UP
    )
    if isinstance(result, Exception):
        raise result

    # DEBUG:
    await asyncio.sleep_ms(3_000)

    onboard_led.on()
    sensor_value: int = get_liquid_sensor_value(liquid_sensor)
    print(f"Publishing liquid sensor value {sensor_value}.")
    await sync_to_async(
        mqtt.publish,
        config.MQTT_TOPIC_ROOT + config.MQTT_TOPIC_LIQUID_SENSOR,
        str(sensor_value).encode(),
    )

    # DEBUG:
    await asyncio.sleep_ms(3_000)

    # await sync_to_async(mqtt.disconnect)

    # onboard_led.off()
    machine.deepsleep(config.SENSOR_SLEEP_AFTER_MEASUREMENT_SEC * 1000)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except OSError as e:
        print(f"Error: {e}")
        machine.deepsleep(config.SENSOR_SLEEP_AFTER_FAILURE_SEC * 1000)
