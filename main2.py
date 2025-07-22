from machine import Pin, PWM
import time

# IR Sensor connected to D4
ir_sensor = Pin(14, Pin.IN)

# Servo on D13
servo = PWM(Pin(12), freq=50)

# Helper function to set angle
def set_angle(angle):
    min_duty = 26   # ~0 deg
    max_duty = 128  # ~180 deg
    duty = int(min_duty + (angle / 180) * (max_duty - min_duty))
    servo.duty(duty)

# Sweep the servo left and right to find black line
def sweep_and_search():
    print("Searching for line...")
    for angle in range(45, 135, 5):
        set_angle(angle)
        time.sleep(0.05)
        if ir_sensor.value() == 0:
            print(f"Black line found at angle {angle}")
            time.sleep(2)  # Stay in the position for 2 seconds
            return angle
    for angle in range(135, 45, -5):
        set_angle(angle)
        time.sleep(0.05)
        if ir_sensor.value() == 0:
            print(f"Black line found at angle {angle}")
            time.sleep(2)  # Stay in the position for 2 seconds
            return angle
    print("No line found")
    return None

# Main loop
while True:
    if ir_sensor.value() == 0:
        print("Line detected at center")
        set_angle(90)  # Go straight
    else:
        result = sweep_and_search()
        if result is not None:
            if result < 90:
                print("Turning Left")
                set_angle(135)
            elif result > 90:
                print("Turning Right")
                set_angle(45)
            time.sleep(2)  # Stay in that turn position
            print("Returning to center")
            set_angle(90)
        else:
            print("Still no line, stop")
            set_angle(90)
    time.sleep(0.2)
