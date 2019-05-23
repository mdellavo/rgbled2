import time
import math
import collections

import pigpio

Led = collections.namedtuple("Led", ["b", "g", "r"])

LEDS = dict([
    ("a", Led(21, 20, 16)),
    ("b", Led(13, 19, 26)),
    ("c", Led(18, 23, 24)),
])


def printf(fmt, *args, **kwargs):
    print(fmt.format(*args, **kwargs))


def test_led(gpio, led):
    print("testing", led)
    for name, pin in zip(led._fields, led):
        print(name, "on pin", pin)
        gpio.write(pin, 1)
        time.sleep(.25)
        gpio.write(pin, 0)
    print()


def off(gpio, leds):
    for led in leds:
        for pin in led:
            gpio.write(pin, 0)


def on(gpio, leds):
    for led in leds:
        for pin in led:
            gpio.write(pin, 1)


def main():
    gpio = pigpio.pi()

    on(gpio, LEDS.values())
    time.sleep(.5)
    off(gpio, LEDS.values())
    time.sleep(.5)

    for led in LEDS.values():
        test_led(gpio, led)

    tick = 0
    try:
        while True:
            for name, led in LEDS.items():
                offset = ord(name) 
                for n, pin in enumerate(led):
                    duty = int((.5 + (math.sin((tick/20) + (offset * 10) + (n * 10)) / 2)) * 255)
                    gpio.set_PWM_dutycycle(pin, duty)
            time.sleep(.017)
            tick += 1


    finally:
        off(gpio, LEDS.values())
        gpio.stop()


if __name__ == "__main__":
    main()
