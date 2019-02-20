#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 13 16:34:22 2018

@author: archit
"""
from datetime import datetime
import os
import math
import numpy as np
import pandas as pd

#date,time,FireStation,RailStation,T1,D1,T2,D2,T2,D3

FIRE_STATION_FILE   =   "FireStations.csv"
RAIL_STATION_FILE   =   "RailStations.csv"
LOAD_FILE           =   "LoadDistribution.txt"
Take_Fastest_Route  =    False
destination         =   "JW Clay Blvd"
source              =   '20'
routes              =    [1]
 
def get_load_distribution():
    dist={}
    with open(LOAD_FILE, 'r') as lf:
        for line in lf:
            line = line.strip('\n')
            machine, start_station, end_station = line.split('\t')
            dist[machine] = [int(start_station), int(end_station)]
        return dist

def read_csv(dataFile, date, target_station, railStation, routes, sortRoutesByTime):
    rows = []
    with open(dataFile, 'r') as df:
        for line in df:
            line = line.strip('\n')
            cols = line.split(',')
            
            if len(cols)-(len(routes)*2) < 4:
                continue
            
            if cols[0] == date and cols[3] == railStation and cols[2]==target_station:
                data = cols[1:3]
                routeInfo = cols[4:]
                routePairs = []
                j = 0
                while j < len(routeInfo):
                    routePairs.append([routeInfo[j], routeInfo[j+1]])
                    j += 2
                
                if sortRoutesByTime:
                    routePairs.sort(key=lambda x : x[0])
                
                for route in routes:
                    data.append(routePairs[route-1])
                
                rows.append(data)
    return rows


def get_fire_stations(fireStationFile, skipfirst=True):
    rows = []
    with open(fireStationFile, 'r') as rf:
        for line in rf:
            if skipfirst:
                skipfirst = False
                continue
            line = line.strip('\n')
            cols = line.split('\t')
            number = cols[0].split()[2]
            data = [number, (float(cols[2]), float(cols[3]))]
            rows.append(data)
        return rows


def get_intervals(traffic):
    N = int(24 * 60 / 5)
    data = [None] * N
    for i in range(len(traffic)):
        ETA = int(traffic[i][2][0])
        t = traffic[i][0]
        dt = datetime.strptime(t, '%H:%M:%S')
        total_seconds = (dt.hour * 60 * 60) + (dt.minute * 60) + dt.second
        interval = math.floor(total_seconds / (5 * 60))
        data[interval] = ETA
    return data
         
    
def read_data(target, machine, railStation, routes, sortRoutesByTime=False):
    filename = '{}.csv'.format(target.date())
    date =  target.date().strftime('%m/%d/%y')
    result_path = os.path.join(os.getcwd(), machine, 'Results', filename)
    traffic = []
    if os.path.exists(result_path):
        traffic = read_csv(result_path, date, source, destination, routes, sortRoutesByTime)
    
    return get_intervals(traffic)
    

def find_target_machine(fireStations, station):
    load_dist = get_load_distribution()
    
    for machine in load_dist.keys():
         r = load_dist[machine]
         f = [fs[0] for fs in fireStations[r[0]-1:r[1]]]
         if station in f:
             return machine

def get_data(month, start, end):
    data = []
    for i in range(start,end+1):
        target_date = datetime(year=2018, month=month, day=i)
        row = read_data(target_date, machine, destination, routes, Take_Fastest_Route)
        row = [target_date.date()] + row
        data.append(row)
    return data

def save(data, filename):
    data = np.asarray(data)
    df = pd.DataFrame(data)
    df.to_csv(filename, header=None, index=None)  


if __name__ == '__main__':

    fireStations = get_fire_stations(FIRE_STATION_FILE)
    machine = find_target_machine(fireStations, source)
    
    
    march = get_data(3,17,31) 
    april = get_data(4,1,30)
    may = get_data(5,1,31)
    june = get_data(6,1,30)
    july = get_data(7,1,9)
    
    train = march + april + may + june + july
    save(train, 'train.csv')
    
    test = get_data(7,10,13)
    save(test, 'test.csv')


 
