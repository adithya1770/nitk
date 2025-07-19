import Jetson.GPIO as GPIO
import time
import os

# Use BCM pin numbering
GPIO.setmode(GPIO.BOARD)  # or GPIO.BCM depending on preference
IR_SENSOR_PIN = 8         # Physical pin 8 (BOARD mode)

# Setup IR sensor input
GPIO.setup(IR_SENSOR_PIN, GPIO.IN)

# ESP32 connection port
ESP32_PORT = "/dev/ttyUSB0"

def run_esp_script(script_name):
    cmd = f"ampy --port {ESP32_PORT} run {script_name}"
    print(f"[Jetson] Running: {cmd}")
    os.system(cmd)

try:
    while True:
        sensor_val = GPIO.input(IR_SENSOR_PIN)

        if sensor_val == GPIO.LOW:
            print("[Jetson] Line detected!")
            run_esp_script("forward.py")
        else:
            print("[Jetson] Line lost!")
            run_esp_script("sweep_check.py")
        
        time.sleep(1)

except KeyboardInterrupt:
    print("\n[Jetson] Exiting...")
finally:
    GPIO.cleanup()
