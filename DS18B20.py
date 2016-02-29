import os
from time import sleep

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
#temp_file = '/sys/bus/w1/devices/28-000006afaa0b/w1_slave'

#jud_Fan = 0
#jud_Heater = 0

def read_temp_raw(temp_file):
    f = open(temp_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp(temp_file):
    lines = read_temp_raw(temp_file)
    while lines[0].strip()[-3:] != 'YES':
        sleep(0.1)
        lines = read_temp_raw(temp_file)
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

def temp(temp_file, delay):
    global jud_Fan
    global jud_Heater

    while True:
        ctemp = read_temp(temp_file)
        print ctemp

        if ctemp >= 26.0 and jud_Fan == 0:
            jud_Fan = 1
            print 'Fan is on'
        elif ctemp <= 25.7 and jud_Fan == 1:
            jud_Fan = 0
            print 'Fan is off'

        if ctemp <= 22.7 and jud_Heater == 0:
            jud_Heater = 1
            print 'Heater is on'
        elif ctemp >=23.1 and jud_Heater == 1:
            jud_Heater = 0
            print 'Heater is off'
        sleep(delay)


def main():
    while True:
        temp = read_temp(temp_file)
        print temp

if __name__ == '__main__':
    main()

