# -*- coding: utf-8 -*-
"""
Created on Thu May  3 11:57:53 2018

@author: aparnami
"""

import numpy as np
import os
import matplotlib.pyplot as plt
import pandas as pd

route="F34toOldCon/dataset-3"
#route="F20toJWClay"
root = os.path.join(os.curdir, "Models", route)

file_alldays = 'residue_alldays.csv'
file_weekdays = 'residue_weekdays.csv'
days = ['Tuesday', 'Wednesday', 'Thursday', 'Friday']
residue_alldays = pd.read_csv(os.path.join(root, file_alldays), header=None, index_col=None)
residue_weekdays = pd.read_csv(os.path.join(root, file_weekdays), header=None, index_col=None)

intervals = int(24 * 60 / 5)
time_labels = []
k = []
for i in range(intervals):
    if (i+1) % 12 == 0:
        h = int((i+1) / 12)
        time_str = '{:02d}:00'.format(h)
        time_labels.append(time_str)
        k.append(i)

def plot(data_alldays, data_weekdays, title):
    x = range(intervals)
    y1 = data_alldays[:,0]
    y2 = data_weekdays[:,0]
    fig, ax = plt.subplots(1, 1, sharex=True)
    ax.plot(x, y1,color='cyan', label='Residue All Days')
    ax.plot(x,y2, color='blue', label='Residue Weekdays')
    ax.fill_between(x, y1, y2, where=y2 >= y1, facecolor='red', interpolate=True)
    ax.fill_between(x, y1, y2, where=y2 <= y1, facecolor='green', interpolate=True)
    ax.set_title(title)
    plt.xlabel('Clock')
    plt.ylabel('Time(s)')
    plt.xticks(k,time_labels,fontsize=7)
    plt.legend(prop={'size': 15})

for i in range(len(days)):
    data_alldays = residue_alldays.iloc[i,:]
    data_weekdays = residue_weekdays.iloc[i,:]
    data_alldays = np.reshape(data_alldays.values, (-1,1))
    data_weekdays = np.reshape(data_weekdays.values, (-1,1))
    plot(data_alldays, data_weekdays, days[i])
   
    

avg_allday_residue = residue_alldays.mean()
avg_allday_residue = np.reshape(avg_allday_residue.values, (-1,1))
avg_weekday_residue = residue_weekdays.mean()
avg_weekday_residue = np.reshape(avg_weekday_residue.values, (-1,1))
plot(avg_allday_residue, avg_weekday_residue, 'Average Residue')



