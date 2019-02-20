# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 19:30:33 2018

@author: aparnami
"""

import time as myclock
import os
import platform
from datetime import datetime, timedelta
from WazeTrafficCalculator import WazeTrafficCalculator

MACHINE             =   platform.node()
MACHINE_FOLDER      =   os.path.join(os.getcwd(), MACHINE)
REQUEST_LOG_PATH    =   os.path.join(MACHINE_FOLDER, "RequestLogs")
CYCLE_LOG_PATH      =   os.path.join(MACHINE_FOLDER, "CycleLogs")
RESULT_PATH         =   os.path.join(MACHINE_FOLDER, "Results")
EXCEPTION_LOG       =   os.path.join(MACHINE_FOLDER, "Exceptions.txt")

FIRE_STATION_FILE   =   "FireStations.csv"
RAIL_STATION_FILE   =   "RailStations.csv"
LOAD_FILE           =   "LoadDistribution.txt"

WAIT_TIME           =   0.4

def init_dirs():
    if not os.path.exists(MACHINE_FOLDER):
        os.makedirs(MACHINE_FOLDER)
    if not os.path.exists(RESULT_PATH):
        os.makedirs(RESULT_PATH)
    if not os.path.exists(REQUEST_LOG_PATH):
        os.makedirs(REQUEST_LOG_PATH)
    if not os.path.exists(CYCLE_LOG_PATH):
        os.makedirs(CYCLE_LOG_PATH)

def get_load_distribution():
    dist={}
    with open(LOAD_FILE, 'r') as lf:
        for line in lf:
            line = line.strip('\n')
            machine, start_station, end_station = line.split('\t')
            dist[machine] = [int(start_station), int(end_station)]
        return dist

def read_fire_station_info(load_info, skipFirst=True):
    source_locs = []
    source_names = []
    info = load_info[MACHINE]
    range_info = range(info[0], info[1]+1)
    i = 0
    with open(FIRE_STATION_FILE, 'r') as sf:
        if skipFirst:
            sf.readline()
        for line in sf:
            i += 1
            if i in range_info:
                line = line.strip('\n')
                cols = line.split('\t')
                name = cols[0].split()[2]
                source_names.append(name)
                source_locs.append(cols[2:4])
    return source_locs, source_names

def read_rail_station_info(skipFirst=True):
    locs = []
    names = []

    with open(RAIL_STATION_FILE, 'r') as sf:
        if skipFirst:
            sf.readline()
        for line in sf:
            line = line.strip('\n')
            cols = line.split('\t')
            names.append(cols[2])
            locs.append(cols[0:2])
    return locs, names

def log(cycle, start_time, end_time):
    LOG_FILE = os.path.join(CYCLE_LOG_PATH, str(start_time.date()) + ".txt")
    
    stime = start_time.time().strftime('%H:%M:%S')
    etime = end_time.time().strftime('%H:%M:%S')
    
    elapsed =  end_time - start_time
    minutes, seconds = divmod(elapsed.total_seconds(), 60)
    hours, minutes = divmod(minutes, 60)
    t = "%d:%02d:%02d" % (hours, minutes, seconds)
    
    with open(LOG_FILE, 'a') as lf:
        text = '{}\t{}\t{}\t{}\n'.format(cycle, stime, etime, t)
        print(text, end='')
        lf.write(text)

def log_exception(e):
    text = '{} {}'.format(datetime.now(), e)
    with open(EXCEPTION_LOG, 'a') as fp:
        fp.write(text)

def process_request(source_loc, source_name, destination_loc,  destination_name):
    
    route = WazeTrafficCalculator(source_loc, destination_loc)
    all_route = route.calc_all_routes_info()
    info = ''    
    
    for k in range(len(all_route)):
        info += '{},{}'.format(all_route[k][0], all_route[k][1])
        if k != len(all_route)-1:
            info += ','
            
    timestamp = datetime.now()
    c_date = timestamp.date().strftime('%m/%d/%y')
    c_time = timestamp.time().strftime('%H:%M:%S')
    result = '{},{},{},{},{}\n'.format(c_date, c_time, source_name, destination_name, info)
    
    return result
    

def process_batch(fp, source_locs, source_names, destination_locs,  destination_names):
    
    n = len(source_locs)
    m = len(destination_locs)
    
    for i in range(n):
        for j in range(m):
            result = ''
            try:
                result = process_request(source_locs[i], source_names[i],
                            destination_locs[j], destination_names[j])
            except Exception as e:
                text = 'RequestException {} {} : {}\n'.format(source_names[i], destination_names[j], e)
                print(text)
                log_exception(text)
            
            fp.write(result)
            myclock.sleep(WAIT_TIME)
    
def main():
    
    init_dirs()
    load_dist = get_load_distribution()
    source_locs, source_names = read_fire_station_info(load_dist)
    destination_locs, destination_names = read_rail_station_info()
    header = 'date,time,FireStation,RailStation,T1,D1,T2,D2,T3,D3\n'
    cycles = 0
    
    def execute_cycle():
        nonlocal cycles
        resultFile = os.path.join(RESULT_PATH, str(datetime.now().date()) + ".csv")
        
        with open(resultFile, 'a') as rf:
            if os.path.getsize(resultFile) == 0:
                cycles = 0
                rf.write(header)
            
            start_time = datetime.now()
            start_min = start_time.minute
            lag_min =  start_min % 5
            if lag_min <= 2:
                next_start_min =  5 - lag_min
            else:
                next_start_min =  10 - lag_min
            next_start = start_time + timedelta(minutes=next_start_min, seconds=-start_time.second, microseconds=-start_time.microsecond)
            
            process_batch(rf, source_locs, source_names, destination_locs, destination_names)
            
            end_time = datetime.now()
            
            
        cycles += 1
        log(cycles, start_time, end_time)
        
        end_time = datetime.now()
        
        if next_start > end_time:
            wait_time = (next_start - end_time).total_seconds()
            myclock.sleep(wait_time)
        
    while True:
        try:
            execute_cycle()
        except Exception as e:
            text = 'CycleException {} : {}\n'.format(cycles, e)
            print(text)
            log_exception(text)
       

if __name__ == '__main__':
    main()
        