from machine import Pin, PWM, UART
import utime

led = Pin(25, Pin.OUT)
uart0 = machine.UART(0, baudrate = 9600, timeout = 1000)
print("UART info: ", uart0)

uart1 = machine.UART(1, baudrate = 9600, timeout = 1000)
print("UART info: ", uart1)

messages = ["hello\n", "world\n"]
i = 0
utime.sleep(1)
while True:
    led.value(1)
    uart0.write(messages[i%2].encode())
    print("Received: " + str(uart1.readline()))
    utime.sleep(1)
    led.value(0)
    utime.sleep(1)
    i += 1
