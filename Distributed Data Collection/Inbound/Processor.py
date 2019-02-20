# -*- coding: utf-8 -*-
"""
Created on Mon Mar  5 18:57:59 2018

@author: aparnami
"""

import os
import subprocess
import platform
import time as myclock
import psutil
from datetime import datetime

MACHINE             =   platform.node()
MACHINE_FOLDER      =   os.path.join(os.getcwd(), MACHINE)
PID_FILE            =   os.path.join(MACHINE_FOLDER, "PID.txt")
INSTRUCTION_FILE    =   os.path.join(MACHINE_FOLDER, "Instructions.txt")
SLEEP_TIME          =   30
PYTHON_PATH         =   ''
SCRIPT_FILE         =   os.path.join(os.getcwd(), 'Main.py')
CHECK_IN_FILE       =   os.path.join(MACHINE_FOLDER, "CheckIn.txt") 


def get_timestamp():
     return datetime.now().strftime('%m/%d/%y %H:%M:%S')
            
def read_pid():
    pid = ''
    if os.path.exists(PID_FILE):
        with open(PID_FILE, 'r') as rf:
            pid = rf.readline().strip('\n')
    return pid

def restart():
    pid = read_pid()
    if pid != '':
        pid = int(pid)
        if psutil.pid_exists(pid):
            try:
                p = psutil.Process(pid)
                p.terminate()
            except Exception as e:
                print(e)
    
    #nohup python3 -u Main.py > /dev/null 2>err.txt &
    subprocess.Popen(['nohup', 'python3', '-u', 'Main.py', '>', '/dev/null', '2>err.txt', '&'])
        
def read_instructions():
    instructions = []
    if os.path.exists(INSTRUCTION_FILE):
        with open(INSTRUCTION_FILE, 'r') as rf:
            for line in rf:
                line = line.strip('\n')
                data = line.split('\t')
                if data[1] == "NEW" and data[2] == MACHINE:
                    instructions.append((data[0], data[3])) #(ID, Instruction)
    return instructions
        
def execute_instructions(instructions):
    status = []
    restarted = False
    for instruction in instructions:
        inst_id, command = instruction
        if command == "RESTART":
            if not restarted:
                restart()
                restarted = True
            status.append((inst_id, "DONE"))
            
    return status
        
def write_status(status):
    instructions = []
    with open(INSTRUCTION_FILE, 'r') as rf:
        instructions = rf.readlines()
    for inst_id, update in status:
        index = int(inst_id) - 1
        instruction = instructions[index]
        instruction = instruction.strip('\n')
        data = instruction.split('\t')
        data[1] = update
        timestamp = get_timestamp()
        timestamp += '\n'
        data.append(timestamp)
        instructions[index] = '\t'.join(data)
    with open(INSTRUCTION_FILE, 'w') as wf:
        wf.writelines(instructions)

def main():
    instructions = read_instructions()
    if len(instructions) > 0:
        status = execute_instructions(instructions)
        if len(status) > 0:
            write_status(status)
    else:
        myclock.sleep(SLEEP_TIME)

def check_in():
    with open(CHECK_IN_FILE, 'w') as wf:
        wf.write(get_timestamp())

if __name__ == '__main__':
    while True:
        check_in()
        main()
        