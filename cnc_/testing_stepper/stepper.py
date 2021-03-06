from machine import Pin, PWM
import utime

DIR_A = 20   # Direction GPIO Pin
STEP_A = 21  # Step GPIO Pin
DIR_B = 2  # Direction GPIO Pin
STEP_B = 3  # Step GPIO Pin
CW = 1     # Clockwise Rotation
CCW = 0    # Counterclockwise Rotation
SPR = 250

direction_a = Pin(DIR_A, Pin.OUT)
step_a = Pin(STEP_A, Pin.OUT)

direction_b = Pin(DIR_B, Pin.OUT)
step_b = Pin(STEP_B, Pin.OUT)

delay = 0.01

utime.sleep(2)
direction_a.value(1)
direction_b.value(1)
#step.value(0)

while True:
    print("Running motor A")
    for x in range(SPR):
        step_a.value(1)
        utime.sleep(delay)
        step_a.value(0)
        utime.sleep(delay)
    
    utime.sleep(1)
    direction_a.value(0)
    for x in range(SPR):
        step_a.value(1)
        utime.sleep(delay)
        step_a.value(0)
        utime.sleep(delay)

    utime.sleep(1)
    direction_a.value(1)

    print("Running motor B")
    for x in range(SPR):
        step_b.value(1)
        utime.sleep(delay)
        step_b.value(0)
        utime.sleep(delay)
    
    utime.sleep(1)
    direction_b.value(0)
    for x in range(SPR):
        step_b.value(1)
        utime.sleep(delay)
        step_b.value(0)
        utime.sleep(delay)

    utime.sleep(1)
    direction_b.value(1)


