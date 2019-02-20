#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 14 20:10:56 2018

@author: archit
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error
from keras.models import load_model
import os
from sklearn.externals import joblib
from datetime import datetime
import matplotlib.patches as mpatches

route="F20toJWClay"
#route="F34toOldCon"
root = os.path.join(os.pardir, "Models", route, "Backup Models")
test_file =   os.path.join(root,"test.csv")
scaler_file = os.path.join(root,'scaler')
model_file = os.path.join(root, 'model')
residue_file = os.path.join(root, 'residue')
dataFile = 'WeatherInfo.csv'

timesteps = 12
threshold = 8
only_weekdays = False

if only_weekdays:
    scaler_file += '_weekdays'
    model_file +=  '_weekdays'
    residue_file += '_weekdays'
else:
    scaler_file += '_alldays'
    model_file += '_alldays'
    residue_file += '_alldays'

def serialize_data(filename):
    df = pd.read_csv(filename, index_col=0, header=None, parse_dates=True)
    if only_weekdays:
        df = df[df.index.weekday<5]
    df.fillna(-1, inplace=True)
    arr = list(df.values)
    all_steps = []
    for row in arr:
        all_steps.extend(row) 
    
    return np.asarray(all_steps).reshape(-1, 1)

def prepare_data(all_steps, refine):
    X = []
    Y = []
    N = len(all_steps)
    for i in range(timesteps, N):
        x = list(all_steps[i-timesteps:i, 0])
        y = all_steps[i, 0]
        #ignore observations with unknown output and number of missing values greater than threshold
        if refine:
            if y != 0 and x.count(0) < threshold:
                X.append(x)
                Y.append(y)
        else:
             X.append(x)
             Y.append(y)
    
    return np.asarray(X),np.asarray(Y)

def get_test_dates(filename):
     df = pd.read_csv(filename, index_col=0, header=None, parse_dates=True)
     return list(df.index.strftime('%m/%d/%y'))

def get_prev_day_timesteps():
    df = pd.read_csv(test_file, index_col=0, header=None, parse_dates=True)
    lastrow = df.tail(1)
    lastrow.fillna(-1, inplace=True)
    x = lastrow.iloc[0,-timesteps:]
    x = list(x)
    x = np.asarray(x).reshape((-1,1))
    return x

prev_day = get_prev_day_timesteps()    
test_set = serialize_data(test_file)
test_set = np.concatenate((prev_day, test_set), axis=0)
test_dates = get_test_dates(test_file)

sc = joblib.load(scaler_file + '.pkl')
test_set_scaled = sc.transform(test_set)

X_test, y_test = prepare_data(test_set_scaled, False)
_, real_traffic = prepare_data(test_set, False)

#Reshaping || data, Batch size, timesteps, indicators 
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

model = load_model(model_file + '.h5')
y_pred = model.predict(X_test)
real_traffic = real_traffic.reshape((-1,1))
pred_traffic = sc.inverse_transform(y_pred)


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

class Weather:
    class Rain:
        LightRain = "light rain"
        ProximityShowerRain = "proximity shower rain"
        ModerateRain = "moderate rain"
        HeavyIntensityRain = "heavy intensity rain"
        VeryHeavyRain =  "very heavy rain"
        FreezingRain = "freezing rain"
        
        @staticmethod
        def Conditions():
            return [Weather.Rain.LightRain, Weather.Rain.ProximityShowerRain,
                    Weather.Rain.ModerateRain, Weather.Rain.HeavyIntensityRain,
                    Weather.Rain.VeryHeavyRain, Weather.Rain.FreezingRain]
        
    class Thunderstorm:
        ProximityTS = "proximity thunderstorm"
        ProximityTSRain = "proximity thunderstorm with rain"
        TS = "thunderstorm"
        TSLightRain = "thunderstorm with light rain"
        TSRain = "thunderstorm with rain"
        TSHeavyRain = "thunderstorm with heavy rain"
        
        @staticmethod
        def Conditions():
            return [Weather.Thunderstorm.ProximityTS, Weather.Thunderstorm.ProximityTSRain,
                    Weather.Thunderstorm.TS, Weather.Thunderstorm.TSLightRain,
                    Weather.Thunderstorm.TSRain, Weather.Thunderstorm.TSHeavyRain]

rain_color = 'g'
thunder_color = 'orange'
patches = {}
for i, cond in enumerate(Weather.Rain.Conditions()):
    patch = mpatches.Patch(facecolor=rain_color, alpha = 0.1 * (i+1), label=cond)
    if cond not in patches:
        patches[cond] = patch

for i, cond in enumerate(Weather.Thunderstorm.Conditions()):
    patch = mpatches.Patch(facecolor=thunder_color, alpha = 0.1 * (i+1), label=cond)
    if cond not in patches:
        patches[cond] = patch

    
for i in range(len(test_dates)):
    if i < 3:
        continue
    handles = {}
    fig = plt.figure(i)
    ax = fig.add_subplot(111)
    start = i * intervals
    gt = real_traffic[start:start+intervals]
    pred = pred_traffic[start:start+intervals]
    traffic= gt!=-1
    error_min = round(mean_squared_error(gt[traffic]/60, pred[traffic]/60),2)
    title = 'Predictons for {}. Error {}'.format(test_dates[i], error_min)
    #gt[gt==-1]=float('nan')
    graph_real = ax.plot(gt, color = 'red', label='Real Traffic')
    graph_pred = ax.plot(pred, color = 'blue', label='Predicted Traffic')
    ax.set_title(title)
    #ax.set_ylim(ymax=900, ymin=400)
    ax.set_xlabel('Clock')
    ax.set_ylabel('Time(s)')
    ax.set_xticks(k)
    ax.set_xticklabels(time_labels)
    
    t_date = datetime.strptime(test_dates[i], '%m/%d/%y')
    df = pd.read_csv(dataFile, parse_dates=['date'])
    t_df = df[df['date'] == t_date]

    con =  (t_df['weather_main'] == 'Thunderstorm') | (t_df['weather_main'] == 'Rain')
    conditions = t_df[con][['time','weather_main','weather_description']]
    conditions['time'] = conditions['time'].apply(lambda x : int(x.split(':')[0]))
    

    for j in range(len(conditions)):
        weather = conditions.iloc[j, 1]
        #description = conditions.iloc[j,2]
        description = weather
        x = conditions.iloc[j, 0] * 12
        y = gt[x]
        d = 6
#        if weather=="Rain":
#            if description == Weather.Rain.LightRain:
#                ax.axvspan(x-d, x+d, facecolor=rain_color, alpha=0.1)
#            elif description == Weather.Rain.ProximityShowerRain:
#                 ax.axvspan(x-d, x+d, facecolor=rain_color, alpha=0.2)
#            elif description == Weather.Rain.ModerateRain:
#                ax.axvspan(x-d, x+d, facecolor=rain_color, alpha=0.3)
#            elif description == Weather.Rain.HeavyIntensityRain or description == Weather.Rain.VeryHeavyRain:
#                ax.axvspan(x-d, x+d, facecolor=rain_color, alpha=0.4)
#            elif description == Weather.Rain.FreezingRain :
#                 ax.axvspan(x-d, x+d, facecolor=rain_color, alpha=0.5)
#        
#        elif weather == "Thunderstorm":
#            if description == Weather.Thunderstorm.ProximityTS:
#                ax.axvspan(x-d, x+d, facecolor=thunder_color, alpha=0.1)
#            elif description == Weather.Thunderstorm.ProximityTSRain:
#                ax.axvspan(x-d, x+d, facecolor=thunder_color, alpha=0.2)
#            elif description == Weather.Thunderstorm.TS:
#                ax.axvspan(x-d, x+d, facecolor=thunder_color, alpha=0.3)
#            elif description == Weather.Thunderstorm.TSLightRain:
#                ax.axvspan(x-d, x+d, facecolor=thunder_color, alpha=0.4)
#            elif description == Weather.Thunderstorm.TSRain:
#                ax.axvspan(x-d, x+d, facecolor=thunder_color, alpha=0.5)
#            elif description == Weather.Thunderstorm.TSHeavyRain:
#                ax.axvspan(x-d, x+d, facecolor=thunder_color, alpha=0.6)
#        
#        if description not in handles:
#            handles[description] = patches[description]
        
#        ax.annotate(description, (x,y), 
#            xytext=(x+(10*(-1)**j), y + (-1)**j * 100),
#            arrowprops=dict(facecolor='black', shrink=0.01, width=1, headwidth=3),
#            size=15)
    
#    residue = np.abs(gt - pred)
#    residual_graph = ax.plot(residue, label='residue')
    
    all_handles = graph_real +  graph_pred #+ list(handles.values()) #+ residual_graph
    #all_handles =  graph_pred #+ list(handles.values()) #+ residual_graph
    ax.legend(handles=all_handles,prop={'size': 15})


    
        
            
    
        
        


    
    

