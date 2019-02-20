#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 14 20:10:56 2018

@author: archit
"""

import pandas as pd
import numpy as np
import os
from sklearn.externals import joblib
import warnings
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout
from keras.callbacks import Callback
from keras import optimizers

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
     

def get_training_data(train_file, scaler_file, timesteps, nextsteps, threshold, only_weekdays):
    training_set = serialize_data(train_file, only_weekdays)
    sc = MinMaxScaler(feature_range=(0,1))
    training_set_scaled = sc.fit_transform(training_set)
    joblib.dump(sc, scaler_file + '.pkl')
    X_train, y_train = prepare_data(training_set_scaled, True, timesteps, nextsteps,threshold)
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
    return X_train, y_train


class EarlyStoppingByLossVal(Callback):
    def __init__(self, monitor='val_loss', value=0.00001, verbose=0):
        super(Callback, self).__init__()
        self.monitor = monitor
        self.value = value
        self.verbose = verbose

    def on_epoch_end(self, epoch, logs={}):
        current = logs.get(self.monitor)
        if current is None:
            warnings.warn("Early stopping requires %s available!" % self.monitor, RuntimeWarning)

        if current < self.value:
            if self.verbose > 0:
                print("Epoch %05d: early stopping THR" % epoch)
            self.model.stop_training = True


def LSTM_Model(layers, input_shape, dropout_reg, units, output_units):
    regressor = Sequential()
    if layers > 1:
        for i in range(1,layers+1):
            if i == 1:
                regressor.add(LSTM(units=units, return_sequences = True, input_shape=input_shape))
                regressor.add(Dropout(dropout_reg))
            elif i == layers:
                regressor.add(LSTM(units=units))
                regressor.add(Dropout(dropout_reg))
            else:
                regressor.add(LSTM(units=units, return_sequences = True))
                regressor.add(Dropout(dropout_reg))
    else:
       regressor.add(LSTM(units=units, input_shape=input_shape))
       regressor.add(Dropout(dropout_reg))
   
    regressor.add(Dense(units=output_units))
    adam = optimizers.Adam(lr=0.01)
    regressor.compile(optimizer = adam, loss = 'mean_squared_error')
    
    return regressor


def train(X_train, y_train, verbose, epochs, layers, model_file,dropout, hidden_units, nextsteps):
    #callbacks = [EarlyStoppingByLossVal(monitor='loss', value=0.0009, verbose=1)]  
    model = LSTM_Model(layers, (X_train.shape[1], 1),dropout, hidden_units, nextsteps)
    model.fit(X_train, y_train, verbose=verbose,epochs=epochs, batch_size=32, callbacks = None)
    model.save(model_file + '_' + str(layers) +  '_' + str(nextsteps) + '.h5')


def train_main(only_weekdays):
    route="F20toJWClay"
    curr_dir= os.getcwd()
    curr_dir_name = os.path.split(curr_dir)[1]
    root = os.path.join(os.pardir, "Models", route)
    train_file = os.path.join(root, "train.csv")
    scaler_file = os.path.join(root,curr_dir_name,'scaler')
    model_file = os.path.join(root,curr_dir_name,'model')

    timesteps = 12
    threshold = 6
    epochs = 20
    nextsteps = 6
    layers = 1
    dropout = 0.2
    hidden_units = 50
    verbose = 1

    if only_weekdays:
        scaler_file += '_weekdays' 
        model_file +=  '_weekdays'
    else:
        scaler_file += '_alldays'
        model_file += '_alldays'

    X_train, y_train = get_training_data(train_file, scaler_file, timesteps, nextsteps,
                                         threshold, only_weekdays)
    
    
    train(X_train, y_train, verbose, epochs, layers, model_file, dropout, 
          hidden_units, nextsteps)

    
    
if __name__ == '__main__':
    train_main(only_weekdays = True)
 