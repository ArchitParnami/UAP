# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 22:45:00 2018

@author: aparnami
"""
import os
import platform
from datetime import datetime, timedelta
import time as clock
import DataCollectionScript

MACHINE             =   platform.node()
MACHINE_FOLDER      =   os.path.join(os.getcwd(), MACHINE)
PID_FILE            =   os.path.join(MACHINE_FOLDER, "PID.txt")


def write_pid():
    if not os.path.exists(MACHINE_FOLDER):
        os.makedirs(MACHINE_FOLDER)
        
    with open(PID_FILE, 'w') as wf:
        PID = str(os.getpid())
        wf.write(PID)

def main():
    current_time = datetime.now()
    next_start_min = 5 - (current_time.minute % 5)
    exec_time = current_time + timedelta(minutes=next_start_min, 
                                         seconds=-current_time.second, 
                                         microseconds=-current_time.microsecond)
    delta =  exec_time - current_time
    wait_time = delta.total_seconds()
    if wait_time >= 0:
        write_pid()
        print("DataCollectionScript will being execution at " + str(exec_time))
        clock.sleep(wait_time)
        print("Executing")
        DataCollectionScript.main()

if __name__ == '__main__':
    main()
    
    
    

