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
sample = 100
x = np.arange(sample)
y = np.sin(2 * np.pi * f * x / Fs)

sensorX = np.array(sample)
sensorY = np.array(sample)
sensorZ = np.array(sample)

breathing = 0

look_back = 20
inputXYZ = InputBuffer(look_back)

sX=0
sY=0
sZ=0
server=None

tframe=0

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

# def calibrate():

#     # time.sleep(1)
#     while True:
#         np.append(sensorX, sX)
#         np.append(sensorY, sY)
#         np.append(sensorZ, sZ)
#         inputXYZ.append(sX,sY,sZ)
#         plt.scatter(x[i], y[i])
#         plt.pause(0.01)
#     plt.show()

def plot():

    xmax= 150
    ymin = 0
    ymax = 200
    tframe=0
    # time.sleep(1)
    plt.xlim(0,xmax)
    plt.ylim(ymin,ymax)
    while True:
        np.append(sensorX, sX)
        np.append(sensorY, sY)
        np.append(sensorZ, sZ)
        # print(sX,sY,sZ)
        plt.scatter(tframe,sX, color="red")
        plt.scatter(tframe,sY, color="green")
        plt.scatter(tframe,sZ, color="blue")

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

  global breathing

  scaler = MinMaxScaler(feature_range=(0, 1))
  # print(scaler.get_params().keys())
  scaler.fit(GetSampleOutData())

  # global inputXYZ
  model = load_model('cnn_control_model.h')

  while True:
    time.sleep(0.01)
    inputXYZ.append(sX,sY,sZ)
    # print(inputXYZ.get().shape)
    XYZ = np.array([inputXYZ.get()])
    
    #DEBUG
    print(XYZ)

    breathing=scaler.inverse_transform(model.predict(XYZ))
    # print(breathing.shape)
    # print(breathing)

def server():
    from pythonosc import dispatcher
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip",
                        default="192.168.1.176", help="The ip to listen on")
    parser.add_argument("--port",
                        type=int, default=5006, help="The port to listen on")
    args = parser.parse_args()
    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/sensor/gravity/x", updateX)
    dispatcher.map("/sensor/gravity/y", updateY)
    dispatcher.map("/sensor/gravity/z", updateZ)

    server = osc_server.ThreadingOSCUDPServer(
    (args.ip, args.port), dispatcher)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()
    if stop():
      server.close()



thread1 = threading.Thread(target = plot)
thread1.start()

  # print("Serving on {}".format(server.server_address))
  # server.serve_forever()

thread2 = threading.Thread(target = server)
thread2.start()



get_breathing()

# calibrate()
# thread2.join()
# print("Stopped listening to OSC commands. Plz stop sending them")

# plt.set_ylim([-1,1])
# plt.plot(y, color="black")
# plt.plot(sensorX, color="red")
# plt.plot(sensorY, color="green")
# plt.plot(sensorZ, color="blue")
# plt.show()

 