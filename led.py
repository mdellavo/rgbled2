import time
import math
import random
import collections

import pigpio

Led = collections.namedtuple("Led", ["b", "g", "r"])

LEDS = dict([
    ("a", Led(21, 20, 16)),
    ("b", Led(13, 19, 26)),
    ("c", Led(18, 23, 24)),
    ("d", Led(17, 27, 22)),
])


def printf(fmt, *args, **kwargs):
    print(fmt.format(*args, **kwargs))


def test_led(gpio, led):
    print("testing", led)
    for name, pin in zip(led._fields, led):
        print(name, "on pin", pin)
        gpio.write(pin, 1)
        time.sleep(1)
        gpio.write(pin, 0)
    print()


def off(gpio, leds):
    for led in leds:
        for pin in led:
            gpio.write(pin, 1)


def on(gpio, leds):
    for led in leds:
        for pin in led:
            gpio.write(pin, 0)


def main():
    gpio = pigpio.pi()

    off(gpio, LEDS.values())

    tick = 0
    try:
        while True:
            for name, led in LEDS.items():
                offset = (-1 + random.random())/10.
                for n, pin in enumerate(led):
                    duty = int((.5 + (math.sin((tick/20) + offset  + (n * 10)) / 2)) * 255)
                    gpio.set_PWM_dutycycle(pin, duty)
            time.sleep(.017)
            tick += 1
    finally:
        off(gpio, LEDS.values())
        gpio.stop()


if __name__ == "__main__":
    main()
