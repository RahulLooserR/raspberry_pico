from machine import Pin, PWM, UART
import utime, math

global num_calibrate
global do_calibration
global pen_up
pen_up = 0
num_calibrate = 2
do_calibration = False

class cnc_:
    def __init__(self) -> None:
        PIN_DIR_A = 2  # Direction GPIO Pin
        PIN_STEP_A = 3  # Step GPIO Pin
        PIN_DIR_B = 20   # Direction GPIO Pin
        PIN_STEP_B = 21  # Step GPIO Pin
        PIN_SERVO = 22 # GP22
        #SPR = 256 # 256 revolution for 40 mm
        self.servo_is_up = True
        #self.SPR = 256 # approximately 256 steps for 40 mm
        self.steps_per_mm = 6.4 # for both motor (~ 256/40) default is 6
        self.x_max = 40 # 40 mm full range
        self.y_max = 40 
        self.current_x = 0
        self.current_y = 0
        
        self.num_step_a = 0
        self.num_step_b = 0

        self.direction_a = Pin(PIN_DIR_A, Pin.OUT)
        self.step_a = Pin(PIN_STEP_A, Pin.OUT)
        self.direction_b = Pin(PIN_DIR_B, Pin.OUT)
        self.step_b = Pin(PIN_STEP_B, Pin.OUT)
    
        # servo init
        self.servo = PWM(Pin(PIN_SERVO))
        self.servo.freq(50)
        self.servo.duty_ns(0)

    # override default servo setting
    def servo_init(self, pin, freq, duty_ns):
        self.servo = PWM(Pin(pin))
        self.servo.freq(freq)
        self.servo.duty_ns(duty_ns)
    
    def servo_degree(self, degrees):
        if degrees > 120: degrees = 120
        if degrees < 30: degrees = 30
        max_duty=9000
        min_duty=1000
        new_duty=min_duty+(max_duty-min_duty)*(degrees/180)
        self.servo.duty_u16(int(new_duty))

    def servo_down(self, degrees=60):
        if self.servo_is_up:
            return
        self.servo_is_up = True
        for degree in range(0, degrees, 1):
            self.servo_degree(degree)
            utime.sleep(0.005)

    def servo_up(self, degrees=60): # degrees should be 180, tweaking
        if not self.servo_is_up:
            return
        self.servo_is_up = False
        for degree in range(degrees, 0, -1):
            self.servo_degree(degree)
            utime.sleep(0.005)
    
    # override default motor A setting
    def motorA_init(self, dir, step):
        self.direction_a = Pin(dir, Pin.OUT)
        self.step_a = Pin(step, Pin.OUT)

    # override default motor B setting
    def motorB_init(self, dir, step):
        self.direction_a = Pin(dir, Pin.OUT)
        self.step_a = Pin(step, Pin.OUT)

    def single_step(self, stepper_motor):
        if stepper_motor == 0:
            #self.direction_a(direction)
            self.step_a.value(0)
            self.step_a.value(1)
            self.num_step_a += 1
            #print("running motor a")
        if stepper_motor == 1:
            #self.direction_b(direction)
            self.step_b.value(0)
            self.step_b.value(1)
            self.num_step_b += 1
            #print("running motor b")

    def print_info(self):
        print("This is yet to be implemented")

def delay(delay_=10000): # 4000 previous setting
    utime.sleep_us(delay_)

class uart_:
    def __init__(self, uart_num=0) -> None:
        self.uart = machine.UART(uart_num, baudrate = 9600, timeout = 1000)
        utime.sleep(1)
    
    def readline(self):
        return str(self.uart.readline(), "utf-8")

    def send_ok(self):
        self.uart.write("OK\n".encode("utf-8"))
    
    def print_info(self):
        print("UART info: ", self.uart)
    
    def any(self):
        return self.uart.any()

def draw_line(x: float, y: float, cnc: cnc_) -> None:
    #print(f'1_current x: {cnc.current_x}')
    #print(f'1_current y: {cnc.current_y}')
    # if (x < 0):
    #     x = 0
    # if (y < 0):
    #     y = 0
    if (x > cnc.x_max):
        x = cnc.x_max
    if (y > cnc.y_max):
        y = cnc.y_max

    # setting direction of motor
    if (cnc.current_x < x):
        cnc.direction_a.value(0)
    else:
        cnc.direction_a.value(1)
    if (cnc.current_y < y):
        cnc.direction_b.value(1)
    else:
        cnc.direction_b.value(0)

    dx = cnc.steps_per_mm * abs(x - cnc.current_x)
    dy = cnc.steps_per_mm * abs(y - cnc.current_y)
    
    over = 0

    if (dx == dy):
        for i in range(round(dx)):
            cnc.single_step(1)
            cnc.single_step(0)
            delay()

    elif (dx > dy):
        for i in range(math.ceil(dx)):
            cnc.single_step(0)  # x-axis movement
            over += dy
            if (over >= dx):
                over -= dx
                cnc.single_step(1) # y-axis movement
            delay()
    
    else:
        for i in range(math.ceil(dy)):
            cnc.single_step(1)  # y-axis movement
            over += dx
            if (over >= dy):
                over -= dy
                cnc.single_step(0) # y-axis movement
            delay()

    # updating position of cnc current x and current y 
    cnc.current_x = x 
    cnc.current_y = y

    # only when calibrating
    if x < 0 and y < 0:
        cnc.current_x = 0
        cnc.current_y = 0

def calibrate(cnc: cnc_) -> None:
    print("Calibrating .....")
    if do_calibration == True:
        x = cnc.current_x
        y = cnc.current_y
        draw_line(-1, -1, cnc)
        draw_line(x, y, cnc)

def process_gcode(cnc: cnc_, gcode: str) -> None:
    global pen_up
    content = gcode.split(";")
    content = content[0].split(" ")    
    
    # linera interpolation
    if content[0] == "G01" or content[0] == "G00":
        if "Z35" in gcode or "Z19" in gcode:
            cnc.servo_up()
            pen_up += 1
            if pen_up % num_calibrate == 0:
                calibrate(cnc)
            return
        if "Z15" in gcode:
            cnc.servo_down()
            return
        if len(content) <= 3:
            return

        x = float(content[2].replace('X',''))
        y = float(content[3].replace('Y',''))
        draw_line(x, y, cnc)


if __name__ == "__main__":
    cnc = cnc_()
    uart = uart_(1)
    uart.print_info()
    #'''
    while True:
        if uart.any():
            gcode = uart.readline()
            uart.send_ok()
            process_gcode(cnc, gcode)