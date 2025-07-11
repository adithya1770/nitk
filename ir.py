import Jetson.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
IR_PIN = 11
GPIO.setup(IR_PIN, GPIO.IN)

try:
    while True:
        if GPIO.input(IR_PIN)==0:
            print("Black line detected")
        else:
            print("White Surface")
        time.sleep(0.2)

except KeyboardInterrupt:
    GPIO.cleanup()
