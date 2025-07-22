from machine import Pin, PWM
import time

servo = PWM(Pin(12), freq=50)

def set_servo_angle(angle):
    min_duty = 26
    max_duty = 128 
    duty = int(min_duty + (angle/ 180) * (max_duty - min_duty))
    servo.duty(duty)

set_servo_angle(45)
time.sleep(2)
set_servo_angle(90)
