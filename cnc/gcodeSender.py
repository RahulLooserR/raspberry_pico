#!/usr/bin/python3

import sys, time
from serial import Serial

if len(sys.argv) not in range (2,3):
    print("Usage: %s <gcode file> <optional: serial port>" % sys.argv[0])
    sys.exit(1)  

if len(sys.argv) == 3:
    serialPort = sys.argv[2]
else:
    serialPort = "/dev/esp32_8266_v3"

gcodeFile = sys.argv[1]

serialp = Serial(serialPort, 9600, timeout=0.01)
time.sleep(1)

#simple method that waits until there is OK detected on the serial port
def wait_for_ok():
    while(1):
        if(serialp.readline() == b'OK\n'):
            break

def read_file(file_name):
    content = open(file_name, "r").read()
    content = content.split('\n')
    content = list(filter(None, content))
    return content

content = read_file(sys.argv[1])

for line in content:
    line = line + "\n"
    serialp.write(line.encode("utf-8"))
    wait_for_ok()