import signal
from gpiozero import Button


def main():
    def pressed():
        print("pressed")

    def released():
        print("released")

    button = Button(12)

    button.when_pressed = pressed
    button.when_released = released
    signal.pause()

if __name__ == "__main__":
    main()
