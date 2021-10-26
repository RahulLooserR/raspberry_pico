#!/usr/bin/python3

import sys, time
from serial import Serial

serialPort = "COM4"
gcodeFile = sys.argv[1]

if len(sys.argv) != 2:
    print("Usage: %s <gcode file>" % sys.argv[0])
    sys.exit(1)

serialp = Serial(serialPort, 9600, timeout=1)
time.sleep(2)

#simple method that waits until there is OK detected on the serial port
def WaitForOK():
    while(1):
        if(serialp.readline() == b'OK\n'):
            break

def read_file(file_name):
    content = open(file_name, "r").read()
    content = content.split('\n')
    content = list(filter(None, content))
    return content

content = read_file("circle_0004.ngc")
#for item in content:
    #print(item)


#while True:

data = "this is test\n"
for i in range(10):
    serialp.write(data.encode())
    time.sleep(1)