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

def serialize_data(filename, only_weekdays):
    df = pd.read_csv(filename, index_col=0, header=None, parse_dates=True)
    if only_weekdays:
        df = df[df.index.weekday<5]
    df.fillna(-1, inplace=True)
    arr = list(df.values)
    all_steps = []
    for row in arr:
        all_steps.extend(row) 
    
    return np.asarray(all_steps).reshape(-1, 1)

def prepare_data(all_steps, refine, timesteps, nextsteps, threshold):
    X = []
    Y = []
    N = len(all_steps)
    for i in range(timesteps, N-nextsteps+1):
        x = list(all_steps[i-timesteps:i, 0])
        y = list(all_steps[i:i+nextsteps, 0])
        #ignore observations with unknown output and number of missing values greater than threshold
        if refine:
            if y.count(0) == 0 and x.count(0) < threshold:
                X.append(x)
                Y.append(y)
        else:
             X.append(x)
             Y.append(y)
    
    return np.asarray(X),np.asarray(Y)

def get_test_dates(filename):
     df = pd.read_csv(filename, index_col=0, header=None, parse_dates=True)
     return list(df.index.strftime('%m/%d/%y'))

def get_prev_day_timesteps(test_file, timesteps):
    df = pd.read_csv(test_file, index_col=0, header=None, parse_dates=True)
    lastrow = df.tail(1)
    lastrow.fillna(-1, inplace=True)
    x = lastrow.iloc[0,-timesteps:]
    x = list(x)
    x = np.asarray(x).reshape((-1,1))
    return x

def predict(X_test, y_test, model_file):
    model = load_model(model_file  + '.h5')
    y_pred = model.predict(X_test)
    #y_pred = X_test[:,11,0]
    #y_pred = y_pred.reshape((-1,1))
    return y_pred

def calculate_error_residue(test_dates, real_traffic, pred_traffic, nextsteps):
    intervals = int(24 * 60 / (5*nextsteps))
    avg_mse = 0
    avg_mape = 0
    error = {}
    all_residues = []
      
    for i in range(len(test_dates)):
        start = i * intervals
        gt = real_traffic[start:start+intervals].reshape(-1,1)
        pred = pred_traffic[start:start+intervals].reshape(-1,1)
        traffic= gt!=-1
        MSE = round(mean_squared_error(gt[traffic]/60, pred[traffic]/60),2)
        MAPE = (gt[traffic] - pred[traffic]) / gt[traffic]
        MAPE = np.abs(MAPE)
        MAPE = (np.sum(MAPE) / len(gt[traffic])) * 100
        MAPE = round(MAPE, 2)
        error[test_dates[i]] = (MSE, MAPE)
        avg_mse += MSE
        avg_mape += MAPE
        
        residue = np.abs(gt - pred)
        residue = residue.T
        all_residues.append(residue)
    
    avg_mse = round(avg_mse / len(test_dates), 2)
    avg_mape = round(avg_mape / len(test_dates), 2)
    error["average"] = (avg_mse, avg_mape)
    
    return error, all_residues
        

#def plot(test_dates, real_traffic, pred_traffic, error, layers, plot_gt, nextsteps, timesteps):
#    intervals = int(24 * 60 / (5*nextsteps))
#    time_labels = []
#    k = []
#    colors = ['blue', 'green', 'orange', 'cyan']
#    for i in range(intervals*nextsteps):
#        if (i+1) % 12 == 0:
#            h = int((i+1) / 12)
#            time_str = '{:02d}:00'.format(h)
#            time_labels.append(time_str)
#            k.append(i)
#            
#    for i in range(len(test_dates)):
#        plt.figure(i)
#        start = i * intervals
#        gt = real_traffic[start:start+intervals].reshape(-1,1)
#        pred = pred_traffic[start:start+intervals].reshape(-1,1)
#        MSE, MAPE = error[test_dates[i]]
#        title = 'Date = {}'.format(test_dates[i])
#        #gt[gt==-1]=float('nan')
#        if plot_gt:
#            plt.plot(gt, color = 'red', label='Real Traffic')
#        prediction_label = 'Layers {}, Timesteps {}, Nextsteps {}, MSE {}, MAPE {}'.format(
#                layers,timesteps, nextsteps, MSE, MAPE)
#        plt.plot(pred, color = colors[nextsteps-1], label=prediction_label)
#        plt.title(title)
#        #plt.ylim(ymax=1000, ymin=200)
#        plt.xlabel('Clock')
#        plt.ylabel('Time(s)')
#        plt.xticks(k,time_labels,fontsize=7)
#        
#        plt.legend(prop={'size': 12})
#        plt.show()
    
def plot(test_dates, real_traffic, pred_traffic, error, layers, plot_gt, nextsteps, timesteps):
    intervals = int(24 * 60 / (5))
    time_labels = []
    k = []
    colors = ['blue', 'green', 'orange', 'cyan'] * 12
    for i in range(intervals):
        if (i+1) % 12 == 0:
            h = int((i+1) / 12)
            time_str = '{:02d}:00'.format(h)
            time_labels.append(time_str)
            k.append(i)
     
    results = []
    for i in range(len(test_dates)):
        plt.figure(i)
        start = i *intervals
        gt = real_traffic[start:start+intervals:nextsteps].reshape(-1,1)
        pred = pred_traffic[start:start+intervals:nextsteps].reshape(-1,1)
        MSE, MAPE = error[test_dates[i]]
        title = 'Date = {}'.format(test_dates[i])
        #gt[gt==-1]=float('nan')
        if plot_gt:
            plt.plot(gt, color = 'red', label='Real Traffic')
        prediction_label = 'Layers {}, Timesteps {}, Nextsteps {}, MSE {}, MAPE {}'.format(
                layers,timesteps, nextsteps, MSE, MAPE)
        plt.plot(pred, color = colors[nextsteps-1], label=prediction_label)
        plt.title(title)
        #plt.ylim(ymax=1000, ymin=200)
        plt.xlabel('Clock')
        plt.ylabel('Time(s)')
        plt.xticks(k,time_labels,fontsize=7)
        
        plt.legend(prop={'size': 12})
        plt.show()
        
        row = pred.reshape((1,-1))
        row  = [test_dates[i]] + list(row[0])
        
        results.append(row)
    
    results = np.asarray(results).reshape((len(test_dates), intervals+1))
    
    return results
      
def save_residue(residue_file, all_residues):
    with open(residue_file + '.csv', 'w') as wf:
        for row in all_residues:
            r = list(row[0])
            x = [str(i) for i in r]
            s = ','.join(x)
            wf.write(s+'\n')

def print_error(test_dates, error):
    result = '{}\t{}\t{}'
    head = result.format("DATE", "MSE", "MAPE")
    print(head)
    for key in test_dates:
        MSE, MAPE = error[key]
        output = result.format(key, MSE, MAPE)
        print(output)
    
    avg_mse, avg_mape = error["average"]
    avg = result.format("Average Error", avg_mse, avg_mape)
    print(avg + '\n')

def test_main(only_weekdays):
    
    route="F20toJWClay"
    curr_dir = os.getcwd()
    curr_dir_name = os.path.split(curr_dir)[1]
    root = os.path.join(os.pardir, "Models", route)
    test_file =   os.path.join(root,"test.csv")
    scaler_file = os.path.join(root,curr_dir_name,'scaler')
    model_file = os.path.join(root,curr_dir_name,'model')
    residue_file = os.path.join(root, 'residue')
    
    timesteps = 12
    threshold = 6
    nextsteps = 6
    
    if only_weekdays:
        scaler_file += '_weekdays'
        model_file +=  '_weekdays'
        residue_file += '_weekdays'
    else:
        scaler_file += '_alldays'
        model_file += '_alldays'
        residue_file += '_alldays'
    
    prev_day = get_prev_day_timesteps(test_file, timesteps)    
    test_set = serialize_data(test_file,only_weekdays)
    test_set = np.concatenate((prev_day, test_set), axis=0)
    test_dates = get_test_dates(test_file)
    
    sc = joblib.load(scaler_file + '.pkl')
    test_set_scaled = sc.transform(test_set)
    
    X_test, y_test = prepare_data(test_set_scaled, False, timesteps, nextsteps, threshold)
    _, real_traffic = prepare_data(test_set, False, timesteps, nextsteps, threshold)
    
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
    
    all_errors = []
    plot_gt = True
    for layers in range(1,2):
        suffix =  '_' + str(layers) +  '_' + str(nextsteps)
        model_filename = model_file + suffix 
        #residue_filename  = residue_file + suffix
    
        y_pred = predict(X_test, y_test, model_filename)
        real_traffic = real_traffic.reshape((-1,nextsteps))
        pred_traffic = sc.inverse_transform(y_pred)
        error, residue = calculate_error_residue(test_dates, real_traffic, pred_traffic, nextsteps)
        plot(test_dates, real_traffic, pred_traffic, error, layers, plot_gt, nextsteps, timesteps)
        #save_residue(residue_filename, residue)
        print_error(test_dates, error)
        errors = []
        for test_date in test_dates:
            errors.append(error[test_date])
        all_errors.append(errors)
        plot_gt = False
    
    return all_errors


if __name__ == '__main__':
    test_main(only_weekdays=True)



        
        


    
    

