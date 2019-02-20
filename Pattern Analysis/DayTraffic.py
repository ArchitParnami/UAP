# -*- coding: utf-8 -*-
"""
Created on Thu May  3 23:38:18 2018

@author: aparnami
"""

import numpy as np
import os
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

route="F34toOldCon"
root = os.path.join(os.curdir, "Models", route)
filepath = os.path.join(root, "train_alldays.csv")

intervals = int(24 * 60 / 5)
time_labels = []
k = []
for i in range(intervals):
    if (i+1) % 12 == 0:
        h = int((i+1) / 12)
        time_str = '{:02d}:00'.format(h)
        time_labels.append(time_str)
        k.append(i)

df = pd.read_csv(filepath, header=None)
dates= pd.date_range(start=datetime(year=2018, month=3, day=17), 
                     end=datetime(year=2018, month=4, day=30))
df.set_index(dates, inplace=True)
df.index = pd.to_datetime(df.index)

days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday','Friday', 'Saturday', 'Sunday']
#fig, axes = plt.subplots(nrows=4, ncols=2, sharex='col')
#fig.delaxes(axes[3][1])
lines = []
for j in range(7):
    daydf = df[df.index.weekday==j]
    stats = daydf.describe()
    std = []
    mean = []
    _max = []
    _min = []
    for i in range(1, len(df.columns)):
        std.append(stats[i]['std'])
        mean.append(stats[i]['mean'])
        _max.append(stats[i]['max'])
        _min.append(stats[i]['min'])
    
    plt.figure(j)
#    line_std, = plt.plot(std, label="Std")
    line_mean, = plt.plot(mean, label="Mean")
    line_min, = plt.plot(_min, label="Min")
    line_max, = plt.plot(_max, label="Max")
    plt.legend(handles=[line_mean, line_min, line_max], loc=1)
    plt.title(days[j])
    plt.xlabel("Clock")
    plt.ylabel("ETA(seconds)")
    plt.xticks(k,time_labels,fontsize=5)
#    p = j//2
#    q = j%2
##    line_std, = axes[p,q].plot(std, label="Std")
#    line_mean,= axes[p,q].plot(mean, label="Mean")
#    line_min, = axes[p,q].plot(_min, label="Min")
#    line_max, = axes[p,q].plot(_max, label="Max")
#    axes[p,q].set_title(days[j])
#    axes[p,q].set_xticks(k)
#    axes[p,q].set_xticklabels(time_labels, fontsize=5)
#    axes[p,q].set_ylabel("ETA(seconds)")
   
#handles, labels = axes[p,q].get_legend_handles_labels()    
#fig.legend(handles, labels, loc='upper center')


    