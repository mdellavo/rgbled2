import signal
import time

from gpiozero import TonalBuzzer, Buzzer
from gpiozero.tones import Tone


b = TonalBuzzer(6)
for i in range(220, 1000):
    print(i)
    b.play(i)
    time.sleep(.01)