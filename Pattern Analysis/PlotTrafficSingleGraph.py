# -*- coding: utf-8 -*-
"""
Created on Thu May  3 23:38:18 2018

@author: aparnami
"""

import numpy as np
import os
import matplotlib.pyplot as plt
import pandas as pd

route="F34toOldCon"
root = os.path.join(os.curdir, "Models", route)
filepath = os.path.join(root, "train.csv")

df = pd.read_csv(filepath, index_col=0, header=None, parse_dates=True)
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday','Friday', 'Saturday', 'Sunday']
colors = ['cyan', 'green', 'red', 'purple', 'blue', 'pink', 'orange', 'yellow']
linestyles = ['-', '--', '-.', ':']

intervals = int(24 * 60 / 5)
time_labels = []
k = []
for i in range(intervals):
    if (i+1) % 12 == 0:
        h = int((i+1) / 12)
        time_str = '{:02d}:00'.format(h)
        time_labels.append(time_str)
        k.append(i)

x = range(intervals)
fig, ax = plt.subplots(7, 1, sharex=True)
ax[0].set_title('Traffic')
for j in range(7): 
    day = df[df.index.weekday==j]
    stats = day.describe()
    std = []
    mean = []
    for i in range(1, len(df.columns)+1):
        std.append(stats[i]['std'])
        mean.append(stats[i]['mean'])
    std = np.asarray(std)
    mean = np.asarray(mean)
    y1 = mean + std
    y2 = mean - std

    #ax.plot(x,y1, color=colors[j])
    #ax.plot(x,y2, color=colors[j])
    ax[j].plot(x, mean, color=colors[j], label=days[j], linewidth=2)
    ax[j].fill_between(x, y1, y2, facecolor=colors[j], interpolate=True, alpha=0.5)
    ax[j].legend()
    ax[j].set_ylim(ymax=800, ymin=400)
    
ax[3].set_ylabel('Time(s)')
plt.xlabel('Clock')
plt.xticks(k,time_labels,fontsize=7)






    