from machine import Pin
import time

ir_sensor = Pin(14, Pin.IN)  # ✅ GPIO 14, not 'D14'

while True:
    print("IR Value:", ir_sensor.value())
    time.sleep(0.5)

