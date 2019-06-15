from gpiozero import DistanceSensor
from time import sleep

TRIGGER_PIN = 5
ECHO_PIN = 6


sensor = DistanceSensor(echo=ECHO_PIN, trigger=TRIGGER_PIN)
while True:
    print('Distance: ', sensor.distance * 100, sensor.max_distance)
    sleep(1)


