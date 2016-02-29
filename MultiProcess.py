import multiprocessing
import os
from time import sleep, ctime

#loops = [4, 2]

class MyProcess(multiprocessing.Process):
    def __init__(self, func, args, name=''):
        multiprocessing.Process.__init__(self, name=name)
        self.func = func
        self.args = args

    def run(self):
        self.func(*self.args)

#def loop(nloop, nsec):
#    print 'start loop', nloop, 'at:', ctime()
#    sleep(nsec)
#    print 'loop', nloop, 'done at:', ctime()

def main():
    print 'starting at:', ctime()
    processes = []
    nloops = range(len(loops))

    for i in nloops:
        t = MyProcess(loop, (i, loops[i]), loop.__name__)
        processes.append(t)

    for i in nloops:
        processes[i].start()

    for i in nloops:
        processes[i].join()

    print 'all DONE at:', ctime

if __name__ == '__main__':
    main()

