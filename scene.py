import time

from gpiozero import Button, RGBLED
# from colorzero import Color

FPS = 60
TICK = 1000./FPS

LED_PINS = [
    (21, 20, 16),
    (13, 19, 26),
    (18, 23, 24),
    (17, 27, 22),
]

BUTTON_PIN = 12
MOTION_SENSOR_PIN = 4


def printf(fmt, *args, **kwargs):
    print(fmt.format(*args, **kwargs))


class Scene:
    def __init__(self, leds):
        self.leds = leds

    def run(self):
        pass  # do stuff


class Rainbow(Scene):
    def run(self):
        pass


class ButtonState:

    LONG_PRESS_TIME = 1
    CLICK_DELAY = .25

    def __init__(self):
        self.pressed_at = None
        self.clicks = 0
        self.clicked_at = 0

    @property
    def pressed(self):
        return self.pressed_at is not None

    def update(self, pressed):
        now = time.time()
        time_since_click = now - self.clicked_at

        if self.pressed and not pressed:
            held_time = now - self.pressed_at
            self.pressed_at = None
            self.on_button_up(held_time)

            if held_time > self.LONG_PRESS_TIME:
                self.on_long_press()
            else:
                self.on_button_press()

            if time_since_click < self.CLICK_DELAY:
                self.clicks += 1

            self.clicked_at = now

        elif not self.pressed and pressed:
            self.pressed_at = now
            self.on_button_down()

        elif time_since_click > self.CLICK_DELAY and self.clicks > 0:
            self.on_repeat_click(self.clicks)
            self.clicks = 0

    def on_button_down(self):
        pass

    def on_button_up(self, held_time):
        pass

    def on_button_press(self):
        pass

    def on_long_press(self):
        pass

    def on_repeat_click(self, clicks):
        pass


def main():
    leds = [RGBLED(r, g, b) for r, g, b in LED_PINS]
    # scene = Rainbow(leds)

    button = Button(BUTTON_PIN)

    class DebugState(ButtonState):
        def on_button_down(self):
            print("down")

        def on_button_up(self, held_time):
            print("up", held_time)

        def on_button_press(self):
            print("press")

        def on_long_press(self):
            print("long press")

        def on_repeat_click(self, clicks):
            print("repeat", clicks)

    button_state = DebugState()

    tick = 0
    last = time.time()
    while True:
        button_state.update(button.is_pressed)

        #scene.update(tick)

        now = time.time()
        delta = now - last
        last = now
        time.sleep(max(TICK - delta, 0) / 1000.)
        tick += 1

if __name__ == "__main__":
    main()
