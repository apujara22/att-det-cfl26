import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

try:
    GPIO.setup(17, GPIO.OUT)
    GPIO.output(17, GPIO.HIGH)
    print("GPIO 17 initialized successfully")
    time.sleep(2)

finally:
    GPIO.cleanup()