from machine import Pin, PWM
import time

# Servo pins
sweep_servo = PWM(Pin(27), freq=50)
drive_servo = PWM(Pin(12), freq=50)

# IR sensor (connected to ESP32)
IR_SENSOR_PIN = 33  # adjust to your ESP32 pin
ir_sensor = Pin(IR_SENSOR_PIN, Pin.IN)

# Helper to convert angle to duty cycle
def set_angle(angle):
    duty = int((angle / 180) * 95) + 20
    sweep_servo.duty(duty)
    time.sleep(0.5)

# Helper to run drive forward
def drive_forward(duration=1.5):
    drive_servo.duty(40)  # may need tuning
    time.sleep(duration)
    drive_servo.duty(77)  # stop

# --- Sweep left ---
set_angle(0)
time.sleep(0.5)
if ir_sensor.value() == 0:
    print("Line found on left")
    drive_forward()
    set_angle(0)
    raise SystemExit()

# --- Sweep right ---
set_angle(180)
time.sleep(0.5)
if ir_sensor.value() == 0:
    print("Line found on right")
    drive_forward()
    set_angle(180)
    raise SystemExit()

# --- Line not found ---
print("Line not found during sweep")
set_angle(90)  # return to center
