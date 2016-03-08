from myThread import MyThread
from MultiProcess import MyProcess
from multiprocessing import Queue, Lock, RLock, Value, Array
from threading import Lock, RLock as tLock, tRLock
from DS18B20 import read_temp
from time import sleep, localtime
import pyfirmata

#addresses for DS18B20
temp1_file = '/sys/bus/w1/devices/28-000006afaa0b/w1_slave'
#temp2_file = '/sys/bus/w1/devices/28-000006b07178/w1_slave'

#Arduino USB port
board = pyfirmata.Arduino('/dev/ttyUSB0')

#digital write pwm(0~1)
pin_Heater = board.get_pin('d:2:o')
pin_CO2 = board.get_pin('d:3:o')
pin_AirPump = board.get_pin('d:4:o')
pin_fan = board.get_pin('d:5:p')
pin_Fertil_1 = board.get_pin('d:6:o')
pin_Fertil_2 = board.get_pin('d:7:o')
pin_Fertil_3 = board.get_pin('d:8:o')
pin_LED = board.get_pin('d:9:p')
#ex)pin2.write(1)


q = Queue()
lock = Lock()
rlock = RLock()
thLock = tLock()
thRLock = tRLock()


#Initialize Arduino
#print 'Initialize Arduino'



# [fan, heater, led, co2, airpump, fer1, fer2, fer3]
judArr = Array('i', [0, 0, 0 ,0 ,0, 0, 0, 0])
masterArr = Array('i', [0, 0, 0 ,0 ,0, 0, 0, 0])


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






#fertilizer
def fertilizer(num, delay, arr):
    if num == 1:
        pin_Fertil_1.write(1)
        lock.acquire()
        arr[5] = 1
        lock.release()
        sleep(delay)
        pin_Fertil_1.write(0)
        lock.acquire()
        arr[5] = 0
        lock.release()
    elif num == 2:
        pin_Fertil_2.write(1)
        lock.acquire()
        arr[6] = 1
        lock.release()
        sleep(delay)
        pin_Fertil_2.write(0)
        lock.acquire()
        arr[6] = 0
        lock.release()
    elif num == 3:
        pin_Fertil_3.write(1)
        lock.acquire()
        arr[7] = 1
        lock.release()
        sleep(delay)
        pin_Fertil_3.write(0)
        lock.acquire()
        arr[7] = 0
        lock.release()
 

 def thFertilizer(num, delay, arr):
     fer = MyThread(fertilizer, (num, delay, arr))
     fer.start()
     fer.join()





#queue
def setCurrentMode(arr, element, mode):
    lock.acquire()
    arr[element] = mode
    lock.release()

		
def savedQueue(q, arr):
    while True:
        if not q.empty():
            output = q.get()
            if output.getMode() == 'on':
                print output.getName() + ' is on'
            elif output.getMode() == 'off':
                print output.getName() + ' is off'
		
            if output.getCode() == 1:
                pin_fan.write(0.5)
                setCurrentMode(arr, 0, 1)
            elif output.getCode() == 11:
                pin_fan.write(0)
                setCurrentMode(arr, 0, 0)
            elif output.getCode() == 2:
                pin_Heater.write(0)
                setCurrentMode(arr, 1, 1)
            elif output.getCode() == 12:
                pin_Heater.write(1)
                setCurrentMode(arr, 1, 0)
            elif output.getCode() == 3:
                pin_LED.write(0)
                setCurrentMode(arr, 2, 1)
            elif output.getCode() == 13:
                pin_LED.write(1)
                setCurrentMode(arr, 2, 0)
            elif output.getCode() == 4:
                pin_CO2.write(0)
                setCurrentMode(arr, 3, 1)
            elif output.getCode() == 14:
                pin_CO2.write(1)
                setCurrentMode(arr, 3, 0)
            elif output.getCode() == 5:
                pin_AirPump.write(0)
                setCurrentMode(arr, 4, 1)
            elif output.getCode() == 15:
                pin_AirPump.write(1)
                setCurrentMode(arr, 4, 0)
            elif output.getCode() == 6:
	            thFertilizer(1, 10, arr)
            elif output.getCode() == 7:
                thFertilizer(2, 10, arr)
            elif output.getCode() == 8:
                thFertilizer(3, 10, arr)




#stand by
def input_mode():
    m = input('Enter a mode: ')
    if m == 0:
        print 'The mode will change to auto'
        return m
    elif m == 1:
        print 'The mode will change to on'
        return m
    elif m == -1:
        print 'The mode will change to off'
        return m
    else :
        print 'Wrong mode.' 
        print 'Enter again from the beginning.'
        print 'This mode will change auto mode.'
        return 0



def standby(mArr):
    i = 0
    while True:
	t = raw_input('Enter a mode you want to change: ')

	if t == 'fan':
	    lock.acquire()
	    mArr[0] = input_mode()
	    lock.release()
	elif t == 'heater':
	    lock.acquire()
	    mArr[1] = input_mode()
	    lock.release()
	elif t == 'led':
	    lock.acquire()
	    mArr[2] = input_mode()
	    lock.release()
	elif t == 'co2':
	    lock.acquire()
	    mArr[3] = input_mode()
	    lock.release()
	elif t == 'airpump':
	    lock.acquire()
	    mArr[4] = input_mode()
	    lock.release()









def queue_standby_Th(q, judArr, masterArr):

    thQueue = MyThread(savedQueue, (q, judArr))
    thStandby = MyThread(standby, masterArr)
    
    thQueue.start()
    thStandby.start()
    
    thQueue.join()
    thStandby.join()










def temp(temp_file, delay, queue, arr, mArr):

    while True:
        ctemp = read_temp(temp_file)
        print ctemp

        if arr[0] == 0:
            if (mArr[0] = 0 and ctemp >= 26.0) or mArr[0] == 1:
                queue.put(Mode('Fan', 'on', 1), 1)
        elif arr[0] == 1:
            if (mArr[0] = 0 and ctemp < 25.7) or mArr[0] == -1:
                queue.put(Mode('Fan', 'off', 11), 1)
			
        if arr[1] == 0:
            if (mArr[1] = 0 and ctemp < 22.7) or mArr[1] == 1:
                queue.put(Mode('Heater', 'on', 2), 1)
        elif arr[1] == 1:
            if (mArr[1] = 0 and ctemp >=23.0) or mArr[1] == -1:
                queue.put(Mode('Heater', 'off', 12), 1)
        
        sleep(delay)
			


def judge(delay, queue, arr, mArr):

    c_time = f_time = localtime()

    while True:
        if c_time[5] != f_time[5]:
            c_time = f_time

            if arr[2] == 0:
                if (c_time[3] >= 7 and c_time[3] < 15 and mArr[2] == 0) or mArr[2] == 1:
                    queue.put(Mode('LED', 'on', 3), 1)
            elif arr[2] == 1:
                if ((c_time[3] < 7 or c_time[3] >= 15) and mArr[2] == 0) or mArr[2] == -1: 
                    queue.put(Mode('LED', 'off', 13), 1)

            if arr[3] == 0:
                if (c_time[3] >= 6 and c_time[3] < 14 and mArr[3] == 0) or mArr[3] == 1:
                queue.put(Mode('CO2', 'on', 4), 1)
            elif arr[3] == 1:
                if ((c_time[3] < 6 or c_time[3] >= 14) and mArr[3] == 0) or mArr[3] == -1:
                    queue.put(Mode('CO2', 'off', 14), 1)
        
            if arr[4] == 0:
                if ((c_time[3] < 6 or c_time[3] >= 15) and mArr[4] == 0) or arr[4] == 1:
                    queue.put(Mode('AirPump', 'on', 5), 1)
            elif arr[4] == 1:
                if (c_time[3] >= 6 and c_time[3] < 15 and mArr[4] == 0) or mArr[4] == -1:
                    queue.put(Mode('AirPump', 'off', 15), 1)
            
            if arr[5] == 0:
                if ((c_time[3] == 6 and c_time[4] == 50 and c_time[5] == 0) and (c_time[6] == 0 or c_time[6] == 2 or c_time[6] == 4))or mArr[5] == 1:
                    queue.put(Mode('Fertilizer1', 'on', 6), 1)
            elif arr[6] == 1:
                if mArr[6] == -1:
                    queue.put(Mode('Fertilizer1', 'off', 7, 1)

            if arr[6] == 0:
                if ((c_time[3] == 6 and c_time[4] == 50 and c_time[5] == 0) and (c_time[6] == 1 or c_time[6] == 3 or c_time[6] == 5))or mArr[6] == 1:
                    queue.put(Mode('Fertilizer1', 'on', 7), 1)
            elif arr[6] == 1:
                if mArr[6] == -1:
                    queue.put(Mode('Fertilizer1', 'off', 7, 1)

            if arr[7] == 0:
                if ((c_time[3] == 6 and c_time[4] == 50 and c_time[5] == 0) and (c_time[6] == 1 or c_time[6] == 3 or c_time[6] == 5))or mArr[7] == 1:
                    queue.put(Mode('Fertilizer1', 'on', 7), 1)
            elif arr[7] == 1:
                if mArr[6] == -1:
                    queue.put(Mode('Fertilizer1', 'off', 7, 1)

        sleep(delay)
        f_time = localtime()

def temp_judge_Th(temp_file, tDelay, jDelay, queue, arr, mArr):

    thTemp = MyThread(temp, (temp1_file, tDelay, queue, arr, mArr))
    thJudge = MyThread(judge, (jDelay, queue, arr, mArr))
    
    thTemp.start()
    thJudge.start()
    
    thTemp.join()
    thTemp.join()



queue_process = MyProcess(queue_standby_Th, (q, judArr, masterArr))
judge_process = MyProcess(temp_judge_Th, (temp1_file, 1, 1, q, judArr, masterArr))






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
    pin_LED.write(1)
    pin_CO2.write(1)
    pin_AirPump.write(1)
    pin_Fertil_1.write(0)
    pin_Fertil_2.write(0)
    pin_Fertil_3.write(0)


