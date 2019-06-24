import abc
import time
import queue
import random

from gpiozero import Button, RGBLED, TonalBuzzer
from gpiozero.tones import Tone
from colorzero import Color, Hue, ease_in_out

FPS_INTERVAL = 30
FPS = 60
TICK = 1000./FPS

LED_PINS = [
    (16, 20, 21),
    (13, 19, 26),
    (18, 23, 24),
    (17, 22, 27),
]
NUM_LEDS = len(LED_PINS)

BUTTON_PIN = 12
BUZZER_PIN = 25


def printf(fmt, *args, **kwargs):
    print(fmt.format(*args, **kwargs))


NOTE_WHOLE, NOTE_HALF, NOTE_QUARTER, NOTE_EIGHTH, NOTE_SIXTEENTH = [4000/(2**i) for i in range(5)]


class ToneCue:
    def __init__(self, at, tone):
        self.at = at
        self.tone = tone

    def apply(self, buzzer):
        buzzer.play(self.tone) if self.tone else buzzer.stop()

    def __str__(self):
        return "<ToneCue(at={}, tone={})>".format(self.at, self.tone)


def play_melody(sound_queue, notes):
    def _enqueue_tone(tone_cue):
        try:
            sound_queue.put_nowait(tone_cue)
        except queue.Full:
            pass

    def _note2tones(t, tone, duration):
        start = ToneCue(t, Tone(tone) if tone else None)
        stop = ToneCue(t + duration, None) if tone else None
        return start, stop

    t = time.time()
    for tone, duration in notes:
        duration /= 1000
        start, stop = _note2tones(t, tone, duration)
        _enqueue_tone(start)
        if stop:
            _enqueue_tone(stop)
        t += duration
    return t


class LightCue:
    def __init__(self, at, indexes, color):
        self.at = at
        self.indexes = indexes
        self.color = color

    def __str__(self):
        return "<LightCue(at={}, indexes={}, color={})>".format(self.at, self.indexes, self.color.hsv)

    def apply(self, leds):
        for index in self.indexes:
            led = leds[index]
            led.color = self.color


class Scene(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def light_cues(self):
        pass


class Rainbow(Scene):
    def light_cues(self):
        i = 0
        color = Color.from_hsv(h=1, s=1, v=1)
        while True:
            yield LightCue(
                at=time.time() + .1,
                indexes=[0, 1, 2],
                color=color
            )
            i += 1
            color += Hue(deg=1)


class Kaleidoscope(Scene):
    def light_cues(self):

        color = Color.from_hsv(h=1, s=1, v=1)
        while True:
            hue = Hue(deg=random.randint(-180, 180))
            next_color = color + hue
            for step_color in color.gradient(next_color, steps=int(round(hue.deg)), easing=ease_in_out):
                yield LightCue(
                    at=time.time() + .05,
                    indexes=[0, 1, 2],
                    color=step_color
                )
            color = next_color


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
    scene = Kaleidoscope()
    button = Button(BUTTON_PIN)
    buzzer = TonalBuzzer(BUZZER_PIN)
    sound_cues = queue.Queue()

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

    def _next_sound_cue():
        rv = None
        try:
            rv = sound_cues.get_nowait()
        except queue.Empty:
            pass
        return rv

    tick = 0
    last = time.time()
    total_time = 0
    light_cues = scene.light_cues()

    play_melody(sound_cues, [
        ("B4", NOTE_SIXTEENTH),
        (None, NOTE_SIXTEENTH),
        ("A4", NOTE_SIXTEENTH),
    ])

    next_light_cue = next(light_cues)
    next_sound_cue = _next_sound_cue()

    while True:
        now = time.time()
        button_state.update(now, button.is_pressed)

        if next_light_cue and now >= next_light_cue.at:
            # print("light cue", next_light_cue)
            next_light_cue.apply(leds)
            next_light_cue = next(light_cues)

        if next_sound_cue and now >= next_sound_cue.at:
            # print("sound cue", next_sound_cue)
            next_sound_cue.apply(buzzer)
            next_sound_cue = _next_sound_cue()

        delta = now - last
        last = now
        sleep_time = max(TICK - delta, 0) / 1000.
        time.sleep(sleep_time)
        tick += 1
        total_time += delta

        if total_time > FPS_INTERVAL:
            print("fps", tick / FPS_INTERVAL)
            total_time = 0
            tick = 0


if __name__ == "__main__":
    main()
