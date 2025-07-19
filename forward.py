from machine import Pin, PWM
import time

servo = PWM(Pin(12), freq=50)

# Forward spin - may need tuning
servo.duty(40)
time.sleep(1.5)

# Stop
servo.duty(77)
