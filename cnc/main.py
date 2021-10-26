#from utils import *
from machine import Pin, PWM, UART
import utime

DIR_A = 20   # Direction GPIO Pin
STEP_A = 21  # Step GPIO Pin
DIR_B = 2  # Direction GPIO Pin
STEP_B = 3  # Step GPIO Pin
CW = 1     # Clockwise Rotation
CCW = 0    # Counterclockwise Rotation
SERVO_PIN = 22 # GP22
SPR = 250
DELAY = 0.01
gcode = ""

def init():
    global direction_a
    global direction_b
    global step_a
    global step_b
    global servo
    global uart 

    direction_a = Pin(DIR_A, Pin.OUT)
    step_a = Pin(STEP_A, Pin.OUT)
    direction_b = Pin(DIR_B, Pin.OUT)
    step_b = Pin(STEP_B, Pin.OUT)
    
    # servo init
    servo = PWM(Pin(22))
    servo.freq(50)
    servo.duty_ns(0)

    # uart init
    uart = machine.UART(0, baudrate = 9600, timeout = 1000)
    print("UART info: ", uart)
    utime.sleep(1)

def run_both_motor():
    direction_a.value(1)
    direction_b.value(1)
    while True:
        for x in range(SPR):
            step_a.value(1)
            step_b.value(1)
            utime.sleep(DELAY)
            step_a.value(0)
            step_b.value(0)
            utime.sleep(DELAY)
    
        utime.sleep(1)
        direction_a.value(0)
        direction_b.value(0)
        for x in range(SPR):
            step_a.value(1)
            step_b.value(1)
            utime.sleep(DELAY)
            step_a.value(0)
            step_b.value(0)
            utime.sleep(DELAY)

        utime.sleep(1)
        direction_a.value(1)
        direction_b.value(1)

def UART_readline(uart):
    return str(uart.readline(), "utf-8")

def UART_send_ok(uart):
    uart.write("OK\n".encode("utf-8"))

def process(gcode):
    pass

init()

while True:
    if uart.any():
        gcode = UART_readline(uart)
        print(gcode)
        UART_send_ok(uart)
        process(gcode)