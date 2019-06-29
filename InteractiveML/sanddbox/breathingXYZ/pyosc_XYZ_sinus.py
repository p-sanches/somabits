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
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from keras.models import load_model



Fs = 125
f = 1
sample =  400
x = np.arange(sample)
y = np.sin(2 * np.pi * f * x / Fs)

# sensorX = np.array(sample)
# sensorY = np.array(sample)
# sensorZ = np.array(sample)

breathing = 0

look_back = 30
n_features=3
inputXYZ = InputBuffer(look_back)

trainXYZ = np.zeros(shape=(sample,3))

sinus = np.zeros(shape=(sample,2))


scalerIn = MinMaxScaler(feature_range=(0, 1))
scalerOut = MinMaxScaler(feature_range=(0, 1))


sX=0
sY=0
sZ=0
server=None

tframe=0

model = None

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
  sX=args[0]

def updateY(address, *args):
  # print(args)
  global sY
  sY=args[0]

def updateZ(address, *args):
  # print(args)
  global sZ
  sZ=args[0]

def calibrate():

    xmax= sample
    ymin = -1
    ymax = 1
    tframe=0

    # plt.xlim(0,xmax)
    # plt.ylim(ymin,ymax)

    global trainXYZ

  # print(scaler.get_params().keys())
    
    # plt.figure(1)
    # time.sleep(1)
    for i in range(len(x)):
        # np.append(sensorX, sX)
        # np.append(sensorY, sY)
        # np.append(sensorZ, sZ)
        
        plt.scatter(x[i], y[i])
        # plt.scatter(x[i], sX)
        plt.pause(0.01)
        trainXYZ[i]= [sX,sY,sZ]
        sinus[i]= [x[i], y[i]]

    # plt.show()
    plt.close()
    # print(trainXYZ)

    print(trainXYZ)

    trainXYZ = scalerIn.fit_transform(trainXYZ)

    print(trainXYZ)
    # sinus= scalerOut.fit_transform(sinus)

    train_data_gen = TimeseriesGenerator(trainXYZ, y,
                               length=look_back, sampling_rate=1,stride=1,
                               batch_size=3)
    model = Sequential()
    model.add(Conv1D(filters=64, kernel_size=3, activation='relu', input_shape=(look_back, n_features)))
    model.add(Conv1D(filters=64, kernel_size=3, activation='relu'))
    # model.add(Conv1D(filters=64, kernel_size=1, activation='relu', input_shape=(look_back, n_features)))
    model.add(Dropout(0.5))
    model.add(MaxPooling1D(pool_size=2))
    model.add(Flatten())
    model.add(Dense(100, activation='relu'))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')


    history = model.fit_generator(train_data_gen, epochs=20).history
    model.save('xyz_model.h')

def plot():

    xmax= sample
    ymin = -2
    ymax = 2
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

        if breathing > 1.5 or breathing < -1.5:
          plt.scatter(tframe,0, color="red")

        plt.scatter(tframe,breathing, color="black")

        tframe+=1
        plt.pause(0.01)
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


calibrate()


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

 