# -*- coding: utf-8 -*-
"""
Created on Thu May  3 11:57:53 2018

@author: aparnami
"""

import numpy as np
import os
import matplotlib.pyplot as plt
import pandas as pd

route="F34toOldCon"
root = os.path.join(os.curdir, "Models", route)

file_alldays = 'residue_alldays.csv'
file_weekdays = 'residue_weekdays.csv'

residue_alldays = pd.read_csv(os.path.join(root, file_alldays), header=None, index_col=None)
residue_alldays = np.reshape(residue_alldays.values, (-1,1))

residue_weekdays = pd.read_csv(os.path.join(root, file_weekdays), header=None, index_col=None)
residue_weekdays = np.reshape(residue_weekdays.values, (-1,1))

#Visualize the results
intervals = int(24 * 60 / 5)
time_labels = []
k = []
for i in range(intervals):
    if (i+1) % 12 == 0:
        h = int((i+1) / 12)
        time_str = '{:02d}:00'.format(h)
        time_labels.append(time_str)
        k.append(i)

plt.figure()
plt.plot(residue_alldays, color = 'cyan', label='Residue All Days')
plt.plot(residue_weekdays, color = 'blue', label='Residue Weekdays')
plt.title('Residue Plots')
plt.xlabel('Clock')
plt.ylabel('Time(s)')
plt.xticks(k,time_labels,fontsize=7)

plt.legend()
plt.show()

x = range(intervals)
y1 = residue_alldays[:,0]
y2 = residue_weekdays[:,0]
fig, ax = plt.subplots(1, 1, sharex=True)
#ax.plot(x, y1, x, y2, color='black')
ax.plot(x, y1,color='cyan', label='Residue All Days')
ax.plot(x,y2, color='blue', label='Residue Weekdays')
ax.fill_between(x, y1, y2, where=y2 >= y1, facecolor='red', interpolate=True)
ax.fill_between(x, y1, y2, where=y2 <= y1, facecolor='green', interpolate=True)
ax.set_title('Residue between Allday vs Weekday Predictions')
plt.xlabel('Clock')
plt.ylabel('Time(s)')
plt.xticks(k,time_labels,fontsize=7)
plt.legend()


