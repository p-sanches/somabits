"""Small example OSC server

This program listens to several addresses, and prints some information about
received packets.
"""
import argparse
import math
import time
import threading
from input_buffer import InputBuffer
from collections import deque
from keras.layers import Dropout

from pythonosc import dispatcher
from pythonosc import osc_server

import numpy as np
import matplotlib.pyplot as plt

import pandas as pa
import numpy as np
from pandas import read_csv
import math
from keras.preprocessing.sequence import TimeseriesGenerator
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import MaxPooling1D
from keras.layers import Conv1D
from keras.layers import Flatten
from keras.layers import LSTM

from statsmodels.tsa.arima_model import ARIMA

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from keras.models import load_model



Fs = 125
f = 1
sample =  200
x = np.arange(sample)
y = 0.5*np.sin((4*np.pi * f * x / Fs))+0.5

actY = np.zeros(sample)

# sensorX = np.array(sample)
# sensorY = np.array(sample)
# sensorZ = np.array(sample)

breathing = 0

look_back = 10
n_features=3
inputXYZ = InputBuffer(look_back, n_features)

trainXYZ = np.zeros(shape=(sample,n_features))

sinus = np.zeros(shape=(sample,2))


scalerIn = MinMaxScaler(feature_range=(0, 1))
scalerOut = MinMaxScaler(feature_range=(0, 1))

sX=0
sY=0
sZ=0
act=0
server=None

tframe=0

model = None

maxRepeated = 2

def print_volume_handler(unused_addr, args, volume):
  print("[{0}] ~ {1}".format(args[0], volume))

def print_compute_handler(unused_addr, args, volume):
  try:
    print("[{0}] ~ {1}".format(args[0], args[1](volume)))
  except ValueError: pass

#get data
def GetSampleOutData():
    return pa.read_csv("output1561706008144.txt", header=0, sep="\t", usecols = ["/actuator/inflate"])

def updateX(address, *args):
  global sX
  # print(args)
  # if(args[0] == sX): print("same x!!!!!")
  sX=args[0]

def updateY(address, *args):
  # print(args)
  global sY
  sY=args[0]

def updateZ(address, *args):
  # print(args)
  global sZ
  sZ=args[0]

def updateAct(address, *args):
  print("act!")
  print(args)
  global act
  act=args[0]

# def calibrateSinus():

#     xmax= sample
#     ymin = -1
#     ymax = 1
#     tframe=0
#     i=0

#     repeated = 0


#     # plt.xlim(0,xmax)
#     # plt.ylim(ymin,ymax)

#     global trainXYZ

#   # print(scaler.get_params().keys())
    
#     # plt.figure(1)
#     # time.sleep(1)
#     while True:
#         # np.append(sensorX, sX)
#         # np.append(sensorY, sY)
#         # np.append(sensorZ, sZ)
#         plt.pause(0.03)

#         if trainXYZ[i-1][0]==sX and trainXYZ[i-1][1]==sY and trainXYZ[i-1][2]==sZ:
#           repeated += 1
#           print(sX,sY,sZ, repeated)
#           if repeated > maxRepeated:
#             continue
#         else: 
#           repeated = 0

        
#         plt.scatter(x[i], y[i])
#         # plt.scatter(x[i], sX)
#         trainXYZ[i]= [sX,sY,sZ]
#         sinus[i]= [x[i], y[i]]


#         i+=1

#         if i not in range(len(x)): 
#           break

#     # plt.show()
#     plt.close()
#     # print(trainXYZ)

#     print(trainXYZ)

#     trainXYZ = scalerIn.fit_transform(trainXYZ)

#     print(trainXYZ)
#     # sinus= scalerOut.fit_transform(sinus)

#     train_data_gen = TimeseriesGenerator(trainXYZ, y,
#                                length=look_back, sampling_rate=1,stride=1,
#                                batch_size=3)
#     model = Sequential()
#     # model.add(Conv1D(filters=64, kernel_size=3, activation='relu', input_shape=(look_back, n_features)))
#     # model.add(Conv1D(filters=64, kernel_size=3, activation='relu'))
#     # # model.add(Conv1D(filters=64, kernel_size=1, activation='relu', input_shape=(look_back, n_features)))
#     # model.add(Dropout(0.5))
#     # model.add(MaxPooling1D(pool_size=2))
#     # model.add(Flatten())
#     # model.add(Dense(100, activation='relu'))
#     # model.add(Dense(1))
#     # model.compile(optimizer='adam', loss='mse')

#     model.add(Conv1D(filters=64, kernel_size=2, activation='relu', input_shape=(look_back, n_features)))
#     model.add(MaxPooling1D(pool_size=2))
#     model.add(Flatten())
#     model.add(Dense(50, activation='relu'))
#     model.add(Dense(1))
#     model.compile(optimizer='adam', loss='mse')

#     # model.add(LSTM(50, activation='relu', return_sequences=True, input_shape=(look_back, n_features)))
#     # model.add(LSTM(50, activation='relu'))
#     # model.add(Dense(1))
#     # model.compile(optimizer='adam', loss='mse')


#     history = model.fit_generator(train_data_gen, epochs=20).history
#     model.save('xyz_model.h')


def calibrateAct():

    xmax= sample
    ymin = -1
    ymax = 1
    tframe=0
    i=0

    repeated = 0


    # plt.xlim(0,xmax)
    # plt.ylim(ymin,ymax)

    global trainXYZ

  # print(scaler.get_params().keys())
    
    # plt.figure(1)
    # time.sleep(1)
    while True:
        # np.append(sensorX, sX)
        # np.append(sensorY, sY)
        # np.append(sensorZ, sZ)
        plt.pause(0.03)

        if np.array_equal(trainXYZ[i-1], [sX,sY,sZ]):
          repeated += 1
          print(sX,sY,sZ, repeated)
          if repeated > maxRepeated:
            continue
        else: 
          repeated = 0

        
        plt.scatter(x[i], act)
        # plt.scatter(x[i], sX)
        trainXYZ[i]= [sX,sY,sZ]
        sinus[i]= [x[i], act]
        actY[i] = act

        i+=1

        if i not in range(len(x)): 
          break

    # plt.show()
    plt.close()
    # print(trainXYZ)

    print(trainXYZ)
    print(trainXYZ.shape)

    trainXYZ = scalerIn.fit_transform(trainXYZ)

    print(trainXYZ)
    # sinus= scalerOut.fit_transform(sinus)

    train_data_gen = TimeseriesGenerator(trainXYZ, actY,
                               length=look_back, sampling_rate=1,stride=1,
                               batch_size=1)
    model = Sequential()
    # model.add(Conv1D(filters=64, kernel_size=3, activation='relu', input_shape=(look_back, n_features)))
    # model.add(Conv1D(filters=64, kernel_size=3, activation='relu'))
    # # model.add(Conv1D(filters=64, kernel_size=1, activation='relu', input_shape=(look_back, n_features)))
    # model.add(Dropout(0.5))
    # model.add(MaxPooling1D(pool_size=2))
    # model.add(Flatten())
    # model.add(Dense(100, activation='relu'))
    # model.add(Dense(1))
    # model.compile(optimizer='adam', loss='mse')

    model.add(Conv1D(filters=64, kernel_size=2, activation='tanh', input_shape=(look_back, n_features)))
    model.add(MaxPooling1D(pool_size=2))
    model.add(Flatten())
    model.add(Dense(50, activation='softmax'))
    # model.add(Dropout(0.3))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse', metrics=['accuracy'])

    # model.add(LSTM(50, activation='relu', return_sequences=True, input_shape=(look_back, n_features)))
    # model.add(LSTM(50, activation='relu'))
    # model.add(Dense(1))
    # model.compile(optimizer='adam', loss='mse')


    history = model.fit_generator(train_data_gen, epochs=10).history


    # model = ARIMA(trainXYZ, order=(look_back,1,0))
    # model_fit = model.fit(disp=0)

    model.save('xyz_model.h')

def plot():

    xmax= sample
    ymin = 0
    ymax = 1.5
    tframe=0
    # time.sleep(1)
    plt.figure(2)
    plt.xlim(0,xmax)
    plt.ylim(ymin,ymax)

    model = load_model('xyz_model.h')

    while True:
        # np.append(sensorX, sX)
        # np.append(sensorY, sY)
        # np.append(sensorZ, sZ)
        # print(sX,sY,sZ)
        # plt.scatter(tframe,sX, color="red")
        # plt.scatter(tframe,sY, color="green")
        # plt.scatter(tframe,sZ, color="blue")
        plt.pause(0.03)

     
        if inputXYZ.repeated([sX,sY,sZ]):
          repeated += 1
          print(sX,sY,sZ, repeated)
          if repeated > maxRepeated:
            continue
        else: 
          repeated = 0

        inputXYZ.append(sX,sY,sZ)

        if not inputXYZ.isFull():
          print (inputXYZ.get())
          continue
        XYZ= inputXYZ.get()
        print(XYZ)

        XYZ = scalerIn.transform(XYZ)
        XYZ = np.array([XYZ])
        breathing=model.predict(XYZ)
        print(breathing.shape)
        print(breathing)

        if breathing > 1.1 or breathing < 0:
          plt.scatter(tframe,0, color="red")

        plt.scatter(tframe,breathing, color="black")

        tframe+=1
        
        if tframe==xmax:
          tframe=0
          plt.clf()
          plt.xlim(0,xmax)
          plt.ylim(ymin,ymax)
    # plt.show()


def get_breathing():

  # global breathing

  global scalerIn
  global inputXYZ
  global model
 
  # global inputXYZ
  model = load_model('xyz_model.h')

  while True:
    time.sleep(0.05)
    inputXYZ.append(sX,sY,sZ)
    # print(inputXYZ.get().shape)

    XYZ= inputXYZ.get()

    XYZ = scalerIn.transform(XYZ)
    
    #DEBUG
    # print(XYZ)

    XYZ = np.array([XYZ])

    # XYZ= scalerIn.transform(XYZ)

    breathing=200*model.predict(XYZ)
    print(breathing.shape)
    print(breathing)

def server():
    from pythonosc import dispatcher
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip",
                        default="192.168.1.176", help="The ip to listen on")
    parser.add_argument("--port",
                        type=int, default=5006, help="The port to listen on")
    args = parser.parse_args()
    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/sensor/x", updateX)
    dispatcher.map("/sensor/y", updateY)
    dispatcher.map("/sensor/z", updateZ)

    dispatcher.map("/actuator/a", updateAct)

    server = osc_server.ThreadingOSCUDPServer(
    (args.ip, args.port), dispatcher)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()
    if stop():
      server.close()





  # print("Serving on {}".format(server.server_address))
  # server.serve_forever()

thread2 = threading.Thread(target = server)
thread2.start()


calibrateAct()


# thread1 = threading.Thread(target = get_breathing)
# thread1.start()
plot()

# calibrate()
# thread2.join()
# print("Stopped listening to OSC commands. Plz stop sending them")

# plt.set_ylim([-1,1])
# plt.plot(y, color="black")
# plt.plot(sensorX, color="red")
# plt.plot(sensorY, color="green")
# plt.plot(sensorZ, color="blue")
# plt.show()

 