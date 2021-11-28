#!/usr/bin/python3

import sys, time
from serial import Serial

if len(sys.argv) not in range (2,3):
    print("Usage: %s <gcode file> <optional: serial port>" % sys.argv[0])
    sys.exit(1)  

if len(sys.argv) == 3:
    serialPort = sys.argv[2]
else:
    serialPort = "/dev/serial_ch341_uart"

gcodeFile = sys.argv[1]

serialp = Serial(serialPort, 9600, timeout=0.01)
time.sleep(1)

#simple method that waits until there is OK detected on the serial port
def wait_for_ok():
    while(1):
        if(serialp.readline() == b'OK\n'):
            break

def read_file(file_name: str):
    content = open(file_name, "r").read()
    content = content.split('\n')
    content = list(filter(None, content))
    return content

def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()

def pre_process_gcode(file_name: str, pen_up_cmd='Z19', num_lines=5):
    line1 = "G00 F300.0 Z19.000; pen up !!Zup"
    line2 = "G00 F300.0 Z15.000; pen down !!Zwork"


    count = 0
    first_index = 0
    last_index = 0
    insert_at = 0
    
    content = read_file(file_name)
    for i in range(len(content)):
        if pen_up_cmd in content[i]:
            first_index = i
            print(f'first {first_index}')
            for j in range(i+1, len(content)):
                if pen_up_cmd in content[j]:
                    last_index = j
                    print(f'last {last_index}')
                    break
            diff = last_index - first_index
            print(f'diff: {diff}')
            if (diff > num_lines):
                if (diff < 2 * num_lines):
                    insert_at =  i + diff / 2
                    # print(f'insert at: {insert_at}')
                    content.insert(int(insert_at), line1)
                    content.insert(int(insert_at+1), line2)
                else:
                    for k in range(1, int(diff / num_lines)):
                        insert_at = i + k * num_lines
                        # print(f'insert at: {insert_at}')
                        content.insert(int(insert_at), line1)
                        content.insert(int(insert_at)+1, line2)
            first_index = 0
            last_index = 0
            
            
    return content


# content = pre_process_gcode(sys.argv[1])
# print(f'content length after: {len(content)}')

# for item in content:
#     print(item)

# sys.exit(0)       
    

content = read_file(sys.argv[1])

filelen = len(content)
num = 0
for line in content:
    line = line + "\n"
    serialp.write(line.encode("utf-8"))
    wait_for_ok()
    num += 1
    progress(num, filelen, ' -> complete')
