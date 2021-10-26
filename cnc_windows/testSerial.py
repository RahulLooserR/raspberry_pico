from machine import Pin, PWM, UART
import utime

uart1 = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9), timeout=10000)
#uart0 = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1), timeout=10000)
uart0 = UART(0, 9600 , parity=None, stop=1, bits=8, tx=Pin(0), rx=Pin(1), timeout=10)
while True:
    #uart0.write("OK\n")
    print("reading")
    utime.sleep(5)
    line = uart0.readline()
    #print(str(line, "utf-8"))
    print(line)
    print("done")
    utime.sleep(1)