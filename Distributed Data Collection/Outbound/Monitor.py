# -*- coding: utf-8 -*-
"""
Created on Sun Mar  4 18:14:01 2018

@author: aparnami
"""

import os
from datetime import datetime, timedelta
import time as myclock

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

LOAD_FILE = "LoadDistribution.txt"
INSTRUCTION_FILE = "Instructions.txt"
CHECK_IN_FILE = "CheckIn.txt" 
PING_TIME = 60
LOG = "LastPing.txt"
MONITOR_START_TIME = None
TIMESTAMP_FORMAT = '%m/%d/%y %H:%M:%S'
PROCESS_CHECK_IN_LIMIT = 4 * 60

class Machine:
    def __init__(self, name, start_node, end_node):
        self.name = name
        self.start_node = start_node
        self.end_node = end_node
        self.root = os.path.join(os.getcwd(), name)
        self.requestLogPath = os.path.join(self.root, "RequestLogs")
        self.cycleLogPath = os.path.join(self.root, "CycleLogs")
        self.resultPath = os.path.join(self.root, "Results")
        self.exceptionLogFile = os.path.join(self.root, "Exceptions.txt")
        self.lastSuccessCycleDateTime = None
        self.numberOfExceptions = 0
        self.sentMails = {'GAP' : []}
        self.newMails = {'GAP' : [], 'EXCEPTIONS' : [], 'STATUS' : []}
        self.INSTRUCTION_FILE = os.path.join(self.root, INSTRUCTION_FILE)
        self.CHECK_IN_FILE = os.path.join(self.root, CHECK_IN_FILE)
        self.status = None
        self.INST_ID = self.get_instruction_count()
    
    def __read_last_cycle(self, filename):
        cycle = []
        if os.path.exists(filename):
            with open(filename, 'r') as lf:
                cycles = lf.readlines()
                if len(cycles) > 0:
                    last_cycle = cycles[-1]
                    cycle = last_cycle.strip('\n')
                    cycle = cycle.split('\t')
        return cycle
        
    def get_last_cycle(self):
        cycle = []
        log_file = os.path.join(self.cycleLogPath, str(datetime.now().date()) + ".txt")
        cycle = self.__read_last_cycle(log_file)
        if len(cycle) == 0:
            previous_day = str((datetime.now() + timedelta(days=-1)).date())
            previous_log_file =  os.path.join(self.cycleLogPath, previous_day + ".txt")
            cycle = self.__read_last_cycle(previous_log_file)
            
        return cycle
    
    def get_request_errors(self, start_time, end_time):
        results = []
        log_file = os.path.join(self.requestLogPath, str(datetime.now().date()) + ".txt")
        if os.path.exists(log_file):
            with open(log_file, 'r') as lf:
                errors = lf.readlines()
                if len(errors) > 0:
                    for error in errors:
                        count = error.count(' ')
                        if count > 0:
                            timestamp = error[:error.index(' ')]
                            timestamp = datetime.strptime(timestamp, '%H:%M:%S')
                            if timestamp >= start_time and timestamp < end_time:
                                results.append(error)
        return results
    
    def get_exceptions(self, filter_date):
        results = []
        if os.path.exists(self.exceptionLogFile):
            with open(self.exceptionLogFile, 'r') as lf:
               exceptions = lf.readlines()
               if len(exceptions) > 0:
                   for exception in exceptions:
                       count = exception.count(' ')
                       if count > 0:
                           exp_date = exception[:exception.index(' ')]
                           exp_date = datetime.strptime(exp_date, '%Y-%m-%d')
                           exp_date = exp_date.date()
                           if exp_date == filter_date:
                               results.append(exception)
        return results
    
    def send_instruction(self, instruction):
        with open(self.INSTRUCTION_FILE, 'a') as fp:
            STATUS = "NEW"
            self.INST_ID += 1
            timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
            INS = '{}\t{}\t{}\t{}\t{}\n'.format(self.INST_ID, STATUS, 
                           self.name, instruction, timestamp)
            fp.write(INS)
    
    def is_active(self):
        if not os.path.exists(self.CHECK_IN_FILE):
            return (False, None)
        
        with open(self.CHECK_IN_FILE, 'r') as rf:
            timestamp_str = rf.readline().strip('\n')
            if timestamp_str == '': #File exists but processor is down
                return (False, None)
            timestamp = datetime.strptime(timestamp_str, TIMESTAMP_FORMAT)
            current = datetime.now()
            gap = (current - timestamp).total_seconds()
            status =  gap < PROCESS_CHECK_IN_LIMIT
            return (status, timestamp_str)
    
    def get_instruction_count(self):
        if os.path.exists(self.INSTRUCTION_FILE):
            with open(self.INSTRUCTION_FILE, 'r') as rf:
                inst = rf.readlines()
                return len(inst)
        else:
            return 0
                
def get_load_distribution():
    dist={}
    with open(LOAD_FILE, 'r') as lf:
        for line in lf:
            line = line.strip('\n')
            machine, start_station, end_station = line.split('\t')
            dist[machine] = [int(start_station), int(end_station)]
    return dist

def send_mail(body, subject='UAP Warning'):

    fromaddr = "uap.bot@gmail.com"
    toaddr = ["aparnami@uncc.edu"]
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = ", ".join(toaddr)
    msg['Subject'] = "OUTBOUND:-" + subject

    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login("uap.bot@gmail.com", "plmoknbji")

    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()

def parse_status(status):
    if status == None:
        return "N.A"
    elif status == True:
        return "ACTIVE"
    else:
        return "INACTIVE"

def log(text):
    with open(LOG, 'w') as wf:
        wf.write(text)
        
def ping(machines):
    
    TIME_LIMIT = 9 * 60
    subject = 'UAP Warning'
    all_text = ''
    
    for machine in machines:
        
        cycle_no = 'NONE'
        cycle_start = 'NONE'
        cycle_end = 'NONE'
        elapsed_time = 'NONE'
        number_of_request_errors = 'NONE'
        current = datetime.now()
        cycle = machine.get_last_cycle()        
        if len(cycle) > 0:
            cycle_no, cycle_start, cycle_end, elapsed_time = cycle[0], cycle[1], cycle[2], cycle[3]
            start_time = datetime.strptime(cycle_start, '%H:%M:%S')
            end_time = datetime.strptime(cycle_end, '%H:%M:%S')
           
            machine.lastSuccessCycleDateTime =  datetime(current.year, current.month, current.day, 
                                                         end_time.hour, end_time.minute, end_time.second)
            
            #get request errors occured in last cycle
            errors = machine.get_request_errors(start_time, end_time)
            number_of_request_errors = len(errors)
        
        #check if any exceptions have occured today
        exceptions = machine.get_exceptions(datetime.now().date())
        number_of_exceptions = len(exceptions)
        
        text = '{}\t{} {} {} {} {} {}\n'.format(machine.name, cycle_no, cycle_start,
                    cycle_end, elapsed_time, number_of_request_errors, number_of_exceptions)
        
        print(text, end='')
        all_text += text
        
        if machine.lastSuccessCycleDateTime == None:
            gap = (current - MONITOR_START_TIME).total_seconds()
        else:
            gap = (current - machine.lastSuccessCycleDateTime).total_seconds()
            
        if gap > TIME_LIMIT:
           if machine.lastSuccessCycleDateTime not in  machine.sentMails['GAP']:
              machine.newMails['GAP'] = [machine.lastSuccessCycleDateTime]
              
        if number_of_exceptions > machine.numberOfExceptions:
            number_of_new_exceptions = number_of_exceptions - machine.numberOfExceptions
            machine.newMails['EXCEPTIONS'] = exceptions[-number_of_new_exceptions:]
            machine.numberOfExceptions= number_of_exceptions
        
        current_status, last_active = machine.is_active()
        if machine.status == None or  machine.status != current_status:
            machine.newMails['STATUS'] = [machine.status, current_status, last_active]
            machine.status = current_status
        
    print()
    log(all_text)
    
    mail_text_gap = ''
    mail_text_exp = ''
    mail_text_status = ''
    
    for machine in machines:
        if len(machine.newMails['GAP']) > 0:
            lastSuccess = machine.newMails['GAP'][0]
            mail_text_gap += '{}\t{}\n'.format(machine.name, lastSuccess)
            machine.newMails['GAP'] = []
            machine.sentMails['GAP'].append(lastSuccess)
            machine.send_instruction("RESTART")
        
        if len(machine.newMails['EXCEPTIONS']) > 0:
            for exception in machine.newMails['EXCEPTIONS']:
                mail_text_exp += '{}\t{}\n'.format(machine.name, exception)
            machine.newMails['EXCEPTIONS'] = []
        
        if len(machine.newMails['STATUS']) > 0:
            old_status, new_status, last_active = machine.newMails['STATUS']
            old_status = parse_status(old_status)
            new_status = parse_status(new_status)
            mail_text_status += '{}\t{}\t{}\t{}\n'.format(machine.name, old_status,
                                 new_status, last_active)
            machine.newMails['STATUS'] = []
            
    
    if mail_text_gap != '':
        subject = "Cycle Time Limit Exceeded"
        body = 'MACHINE \t\tLAST FINISHED\n' + mail_text_gap
        send_mail(body, subject)
        
    if mail_text_exp != '':
        subject = "New Exceptions Encountered"
        body = 'MACHINE \tEXCEPTION\n' + mail_text_exp
        send_mail(body, subject)
    
    if mail_text_status != '':
        subject = "Machine State Changed"
        body = 'MACHINE\tOLD STATUS\tNEW STATUS\tLAST ACTIVE\n' + mail_text_status
        send_mail(body, subject)
         
   

def main():
    dist = get_load_distribution()
    machines = []
    for key in dist.keys():
        load = dist[key]
        machine = Machine(key, load[0], load[1])
        machines.append(machine)
    
    global MONITOR_START_TIME
    MONITOR_START_TIME = datetime.now()
    
    while True:
        ping(machines)
        myclock.sleep(PING_TIME)
        

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        subject = "Monitor Shutting Down"
        body = "The following exception has caused the monitor to crash:\n" + str(e)
        log(str(e))
        send_mail(body, subject)