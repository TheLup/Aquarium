from myThread import MyThread
from MultiProcess import MyProcess
from multiprocessing import Queue, Lock, RLock
from DS18B20 import read_temp
from time import sleep
import time
import pyfirmata

#addresses for DS18B20
temp1_file = '/sys/bus/w1/devices/28-000006afaa0b/w1_slave'
temp2_file = '/sys/bus/w1/devices/28-000006b07178/w1_slave'

#Slave addresses
board = pyfirmata.Arduino('/dev/ttyUSB0')
#digital write
pin_Heater = board.get_pin('d:2:o')
pin_CO2 = board.get_pin('d:3:o')
pin_AirPump = board.get_pin('d:4:o')
#pwm write 0~1
pin_fan = board.get_pin('d:5:p')
pin_LED = board.get_pin('d:9:p')

#pin2.write(1)

q = Queue(20)
lock = Lock()
rlock = RLock()

#Initialize Arduino
print 'Initialize Arduino'



class Mode():
    def __init__(self, name, mode, code):
        self.name = name
        self.mode = mode
        self.code = code

    def setName(self, name):
        self.name = name
    def setMode(self, mode):
        self.mode = mode
    def setCode(self, code):
        self.code = code
    def getName(self):
        return self.name
    def getMode(self):
        return self.mode
    def getCode(self):
        return self.code

		
def savedQueue(q, delay):
    global jud_Fan
    global jud_Heater
    global jud_LED
    global jud_CO2
    global jud_AirPump

    while True:
        if not q.empty():
            output = q.get()
            print 
            if output.getMode() == 'on':
                print output.getName() + ' is on'
                sleep(delay)
            elif output.getMode() == 'off':
                print output.getName() + ' is off'
                sleep(delay)
		
            if output.getCode() == 1:
                pin_fan.write(0.5)
                jud_Fan = 1
            elif output.getCode() == 11:
                pin_fan.write(0)
                jud_Fan = 0
            elif output.getCode() == 2:
                pin_Heater.write(0)
                jud_Heater = 1
            elif output.getCode() == 12:
                pin_Heater.write(1)
                jud_Heater = 0
            elif output.getCode() == 3:
                pin_LED.write(1)
                jud_LED = 1
            elif output.getCode() == 13:
                pin_LED.write(0)
                jud_LED = 0
            elif output.getCode() == 4:
                pin_CO2.write(0)
                jud_CO2 = 1
            elif output.getCode() == 14:
                pin_CO2.write(1)
                jud_CO2 = 0
            elif output.getCode() == 5:
                pin_AirPump.write(0)
                jud_AirPump = 1
            elif output.getCode() == 15:
                pin_AirPump.write(1)
                jud_AirPump = 0


queue_thread = MyProcess(savedQueue, (q, 3), savedQueue.__name__)

def temp(temp_file, delay, queue):
    global jud_Fan
    global jud_Heater

    while True:
        ctemp = read_temp(temp_file)
        print ctemp

        if ctemp >= 26.0 and jud_Fan == 0:
            queue.put(Mode('Fan', 'on', 1), 1)
        elif ctemp <= 25.7 and jud_Fan == 1:
            queue.put(Mode('Fan', 'off', 11), 1)
			
        if ctemp <= 22.7 and jud_Heater == 0:
            queue.put(Mode('Heater', 'on', 2), 1)
        elif ctemp >=23.1 and jud_Heater == 1:
            queue.put(Mode('Heater', 'off', 12), 1)
        
        sleep(delay)
			


temp_thread = MyProcess(temp, (temp1_file, 0.5, q), temp.__name__)

def light(delay, queue):

    c_time = f_time = time.localtime()

    while True:
        if c_time[5] != f_time[5]:
            c_time = f_time

            if c_time[3] >= 7 and c_time[3] < 15 and jud_LED == 0:
                queue.put(Mode('LED', 'on', 3), 1)
            elif (c_time[3] < 7 or c_time[3] >= 15) and jud_LED == 1:
                queue.put(Mode('LED', 'off', 13), 1)

            if c_time[3] >= 6 and c_time[3] < 14 and jud_CO2 == 0:
                queue.put(Mode('CO2', 'on', 4), 1)
            elif (c_time[3] < 6 or c_time[3] >= 14) and jud_CO2 == 1:
                queue.put(Mode('CO2', 'off', 14), 1)
        
            if (c_time[3] < 6 or c_time[3] >= 15) and jud_AirPump == 0:
                queue.put(Mode('AirPump', 'on', 5), 1)
            elif c_time[3] >= 6 and c_time[3] < 15 and jud_AirPump == 1:
                queue.put(Mode('AirPump', 'off', 15), 1)
        
        sleep(delay)
        f_time = time.localtime()

light_thread = MyProcess(light, (1, q), light.__name__)

def info(delay, queue):
    global jud_Fan
    global jud_Heater
    global jud_LED
    global jud_CO2
    global jud_AirPump

    while True:
        print 'Fan: ', jud_Fan
        print 'Heater: ', jud_Heater
        print 'LED: ', jud_LED
        print 'CO2: ', jud_CO2
        print 'AirPump: ', jud_AirPump
        sleep(delay)

info_thread = MyProcess(info,(1, q), info.__name__)

jud_Fan = 0
jud_Heater = 0
jud_LED = 0
jud_CO2 = 0
jud_AirPump = 0

c_time = time.localtime()

try:
    temp_thread.start()
    queue_thread.start()
    light_thread.start()

    temp_thread.join()
    queue_thread.join()
    light_thread.join()

except KeyboardInterrupt:
    pin_fan.write(0)
    pin_Heater.write(1)
    pin_LED.write(0)
    pin_CO2.write(1)
    pin_AirPump.write(1)
