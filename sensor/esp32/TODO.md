Писать в лог на примере p1-meter.
Настроить mosquitto на работу с пользователем.
Считывать 3 раза с интервалом в 3 секунды, усреднять, округлять и отправлять.


Использовать celery (очередь задач) для выполнения фоновых задач (отправки сообщений в telegram).


from machine import Pin
p4 = Pin(4, Pin.IN, Pin.PULL_UP) # enable internal pull-up resistor


If the pull resistors are not actively required during deep-sleep and
are likely to cause current leakage (for example a pull-up resistor
is connected to ground through a switch), then they should be disabled
to save power before entering deep-sleep mode:

from machine import Pin, deepsleep

# configure input RTC pin with pull-up on boot
pin = Pin(2, Pin.IN, Pin.PULL_UP)

# disable pull-up and put the device to sleep for 10 seconds
pin.init(pull=None)
machine.deepsleep(10_000)




There’s a higher-level abstraction machine.Signal which can be used to invert a pin. Useful for illuminating active-low LEDs using on() or value(1).




from machine import Pin, Signal

# Suppose you have an active-high LED on pin 0
led1_pin = Pin(0, Pin.OUT)
# ... and active-low LED on pin 1
led2_pin = Pin(1, Pin.OUT)

# Now to light up both of them using Pin class, you'll need to set
# them to different values
led1_pin.value(1)
led2_pin.value(0)

# Signal class allows to abstract away active-high/active-low
# difference
led1 = Signal(led1_pin, invert=False)
led2 = Signal(led2_pin, invert=True)

# Now lighting up them looks the same
led1.value(1)
led2.value(1)

# Even better:
led1.on()
led2.on()




https://docs.micropython.org/en/v1.22.0/library/asyncio.html

import asyncio

async def blink(led, period_ms):
    while True:
        led.on()
        await asyncio.sleep_ms(5)
        led.off()
        await asyncio.sleep_ms(period_ms)

async def main(led1, led2):
    asyncio.create_task(blink(led1, 700))
    asyncio.create_task(blink(led2, 400))
    await asyncio.sleep_ms(10_000)

# Running on a pyboard
from pyb import LED
asyncio.run(main(LED(1), LED(2)))

# Running on a generic board
from machine import Pin
asyncio.run(main(Pin(1), Pin(2)))