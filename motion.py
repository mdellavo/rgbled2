from gpiozero import MotionSensor, LED
from signal import pause

pir = MotionSensor(4)

def motion():
    print("motion!")

def no_motion():
    print("no motion")


pir.when_motion = motion
pir.when_no_motion = no_motion

pause()
