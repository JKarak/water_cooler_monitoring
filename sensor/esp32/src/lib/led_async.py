import asyncio
from machine import Signal


class AsyncLED:
    def __init__(self, led_signal: Signal):
        self._led: Signal = led_signal
        self._rate: float = 0
        self._task = asyncio.create_task(self.run())

    async def run(self):
        while True:
            if self._rate <= 0:
                await asyncio.sleep_ms(200)
            else:
                self._led.value((1, 0)[self._led.value()])
                await asyncio.sleep_ms(int(1_000 / self._rate))

    def flash(self, rate: float):
        self._rate = rate

    def on(self):
        self._led.on()
        self._rate = 0

    def off(self):
        self._led.off()
        self._rate = 0
