from myThread import MyThread
from MultiProcess import MyProcess
from multiprocessing import Queue, Lock, RLock
from DS18B20 import read_temp
from time import sleep
import time
import pyfirmata

#addresses for DS18B20
temp1_file = '/sys/bus/w1/devices/28-000006afaa0b/w1_slave'
#temp2_file = '/sys/bus/w1/devices/28-000006b07178/w1_slave'

#Slave addresses
board = pyfirmata.Arduino('/dev/ttyUSB0')

#digital write pwm(0~1)
pin_Heater = board.get_pin('d:2:o')
pin_CO2 = board.get_pin('d:3:o')
pin_AirPump = board.get_pin('d:4:o')
pin_fan = board.get_pin('d:5:p')
#pin_Fertil_1 = board.get_pin('d:6:o')
#pin_Fertil_2 = board.get_pin('d:7:o')
#pin_Fertil_3 = board.get_pin('d:8:o')
pin_LED = board.get_pin('d:9:p')
#ex)pin2.write(1)


q = Queue()
lock = Lock()
rlock = RLock()

#Initialize Arduino
#print 'Initialize Arduino'


jud_Fan = 0
jud_Heater = 0
jud_LED = 0
jud_CO2 = 0
jud_AirPump = 0

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

            if output.getMode() == 'on':
                print output.getName() + ' is on'
            elif output.getMode() == 'off':
                print output.getName() + ' is off'
		
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
			


def judge(delay, queue):

    global jud_LED
    global jud_CO2
    global jud_AirPump

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

def temp_judge_Th(temp_file, tDelay, jDelay, queue):
    thTemp = MyThread(temp, (temp1_file, tDelay, queue), temp.__name__)
    thJudge = MyThread(judge, (jDelay, queue), judge.__name__)
    
    thTemp.start()
    thJudge.start()
    
    thTemp.join()
    thTemp.join()



queue_process = MyProcess(savedQueue, (q, 3), savedQueue.__name__)
judge_process = MyProcess(temp_judge_Th, (temp1_file, 1, 1, q), temp_judge_Th.__name__)



c_time = time.localtime()

try:
    queue_process.start()
    judge_process.start()

    queue_process.join()
    judge_process.join()

except KeyboardInterrupt:
    judge_process.terminate()
    queue_process.terminate()
    pin_fan.write(0)
    pin_Heater.write(1)
    pin_LED.write(0)
    pin_CO2.write(1)
    pin_AirPump.write(1)
#    pin_Fertil_1.write(0)
#    pin_Fertil_2.write(0)
#    pin_Fertil_3.write(0)


