import time
import abc

from gpiozero import Button, RGBLED, TonalBuzzer
from gpiozero.tones import Tone
from colorzero import Color

Color.repr_style = "rgb"

FPS = 60
TICK = 1000./FPS

LED_PINS = [
    (21, 20, 16),
    (13, 19, 26),
    (18, 23, 24),
    (17, 27, 22),
]

BUTTON_PIN = 12
BUZZER_PIN = 25


def printf(fmt, *args, **kwargs):
    print(fmt.format(*args, **kwargs))


class LightCue:
    def __init__(self, at, leds, color):
        self.at = at
        self.leds = leds
        self.color = color

    def __str__(self):
        return "<LightCue(at={}, color={})>".format(self.at, self.color)

    def apply(self):
        for led in self.leds:
            led.color = self.color


class Scene(metaclass=abc.ABCMeta):
    def __init__(self, leds):
        self.leds = leds

    @abc.abstractmethod
    def light_cues(self):
        pass


class Rainbow(Scene):
    def light_cues(self):
        i = 0
        colors = (
                list(Color(1, 0, 0).gradient(Color(0, 1, 0), steps=100)) +
                list(Color(0, 1, 0).gradient(Color(0, 0, 1), steps=100)) +
                list(Color(0, 0, 1).gradient(Color(1, 0, 0), steps=100))
        )
        while True:
            yield LightCue(
                at=time.time() + .1,
                leds=self.leds,
                color=colors[i % len(colors)]
            )
            i += 1


# FIXME factor out handler interface
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

    def update(self, now, pressed):
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
    scene = Rainbow(leds)
    button = Button(BUTTON_PIN)
    buzzer = TonalBuzzer(BUZZER_PIN)

    class DebugState(ButtonState):
        def on_button_down(self):
            print("down")
            buzzer.play(Tone("B4"))

        def on_button_up(self, held_time):
            print("up", held_time)
            buzzer.stop()

        def on_button_press(self):
            print("press")
            #buzzer.play(Tone("C4"))

        def on_long_press(self):
            print("long press")
            #buzzer.play(Tone("D4"))

        def on_repeat_click(self, clicks):
            print("repeat", clicks)
            #buzzer.play(Tone("E4"))

    button_state = DebugState()

    tick = 0
    last = time.time()
    light_cues = scene.light_cues()
    next_light_cue = next(light_cues)
    while True:
        now = time.time()
        button_state.update(now, button.is_pressed)

        if now >= next_light_cue.at:
            print("light cue", next_light_cue)
            next_light_cue.apply()
            next_light_cue = next(light_cues)

        delta = now - last
        last = now
        time.sleep(max(TICK - delta, 0) / 1000.)
        tick += 1


if __name__ == "__main__":
    main()
