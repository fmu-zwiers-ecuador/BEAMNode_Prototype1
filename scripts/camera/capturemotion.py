# This script should read from a motion detector plugged into GPIO pin 4 and take a picture using RPI camera modurle

from picamera2 import Picamera2
from gpiozero import MotionSensor
import time

print("WAITING FOR MOTION")
# set up motion sensor
pir = MotionSensor(4)

# set up picamera

picam = Picamera2()
camera_config = picam.create_still_configuration(main={"size": (1920, 1080)}, lores={"size": (640,480)}, display="lores")

picam.start()

time.sleep(1)

i = 0

while True:
    pir.wait_for_motion()
    print("MOTION FOUND, CAPTURING IMAGE")
    picam.capture.file(f"./pics/motionpic{i}.jpg")
    i = i + 1
    time.sleep(1)

picam.stop()
