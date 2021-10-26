from machine import Pin, PWM
from time import sleep

servoPin = PWM(Pin(22))
servoPin.freq(50)
servoPin.duty_u16(0)

led = Pin(25, Pin.OUT)

def servo(degrees):
    if degrees > 170: degrees=180
    if degrees < 10: degrees=10
    maxDuty=9000
    minDuty=1000
    newDuty=minDuty+(maxDuty-minDuty)*(degrees/170)
    servoPin.duty_u16(int(newDuty))

sleep(20)
while True:
    led.toggle()
    for degree in range(10,180,1):
        servo(degree)
        sleep(0.01)
        print("increasing -- "+str(degree))

    led.toggle()
    for degree in range(180, 10, -1):
        servo(degree)
        sleep(0.01)
        print("decreasing -- "+str(degree))