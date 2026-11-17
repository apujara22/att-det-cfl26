import RPi.GPIO as GPIO
import time

LINES = {"REG3V3": 17, "GRPA3V3": 27, "GRPB3V3": 22, "I2CMUX": 23}

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(LINES["REG3V3"], GPIO.OUT)
GPIO.setup(LINES["GRPA3V3"], GPIO.OUT)
GPIO.setup(LINES["GRPB3V3"], GPIO.OUT)
GPIO.setup(LINES["I2CMUX"], GPIO.OUT)

def high(line):
    if line not in LINES:
        raise Exception(f"available lines are: {[x for item in LINES]}")
    
    gpioPin = LINES[line]
    GPIO.output(gpioPin, GPIO.HIGH) 

def low(line):
    if line not in LINES:
        raise Exception(f"available lines are: {[x for item in LINES]}")
    
    gpioPin = LINES[line]
    GPIO.output(gpioPin, GPIO.LOW) 

def cycle(line, off_time=3):
    if line not in LINES:
        raise Exception(f"available lines are: {[x for item in LINES]}")

    gpioPin = LINES[line]
    GPIO.output(gpioPin, GPIO.HIGH)
    time.sleep(off_time)
    GPIO.output(gpioPin, GPIO.LOW)

low("REG3V3")
low("GRPA3V3")
low("GRPB3V3")
low("I2CMUX")
