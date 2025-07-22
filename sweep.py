from machine import Pin, PWM
from time import sleep

# Servo connected to D13 (GPIO13)
servo = PWM(Pin(13), freq=50)

# Function to set angle (maps 0-180° to duty cycle)
def set_angle(angle):
    duty = int((angle / 180) * 102 + 26)  # Map angle to duty (approx. 26–128)
    servo.duty(duty)

# Sweep from 0° to 180° and back
for _ in range(2):
    for angle in range(0, 181, 5):  # 0° to 180° in steps
        set_angle(angle)
        sleep(0.03)

    for angle in range(180, -1, -5):  # 180° to 0° in steps
        set_angle(angle)
        sleep(0.03)

set_angle(90)
