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


from pythonosc import osc_message_builder
from pythonosc import udp_client


int direct_actuation = 0;

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

look_back = 30
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

def updtouchOSC (address, *args):
  global sX
  global sY
  global sZ
  # print("touchOCC")
  # print(args)
  # if(args[0] == sX): print("same x!!!!!")
  sX=args[0]
  sY=args[1]
  sZ=args[2]

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

  direct_actuation = 1 #someone is directly controlling the actuator
  
  global act
  act=args[0]
  print(act)

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

#         client.send_message("/actuator/inflate", (y[i]*200)-100)


#         i+=1

#         if i not in range(len(x)): 
#           break

#     # plt.show()
#     plt.close()
#     client.send_message("/actuator/inflate", 0.0)
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
    ymax = 10
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
        client.send_message("/actuator/inflate", act*200-100)
        # plt.scatter(x[i], sX)
        # plt.scatter(x[i], sY)
        # plt.scatter(x[i], sZ)
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
    model.add(Dense(50, activation='tanh'))
    model.add(Dropout(0.1))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')
    #,metrics=['accuracy'])

    # model.add(LSTM(50, activation='relu', return_sequences=True, input_shape=(look_back, n_features)))
    # model.add(LSTM(50, activation='softmax'))
    # model.add(Dense(1))
    # model.compile(optimizer='adam', loss='mse')


    history = model.fit_generator(train_data_gen, epochs=50).history


    # model = ARIMA(trainXYZ, order=(look_back,1,0))
    # model_fit = model.fit(disp=0)

    model.save('xyz_model.h')

    direct_actuation = 0; #to start predicting when training is over

def plot():

    xmax= sample
    ymin = 0
    ymax = 1
    tframe=0
    # time.sleep(1)
    plt.figure(2)
    plt.xlim(0,xmax)
    plt.ylim(ymin,ymax)

    model = load_model('xyz_model.h')

    client = udp_client.SimpleUDPClient("127.0.0.1", 32000)

    nr_samples_retrain = 0
    in_training= 0
    trainXYZ

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




        #COMMENT ALL THIS UNTIL THE COMMENT BELOW

        if direct_actuation = 1: #if the user touched the actuation button, then we have to go into re-training mode
        	in_training = 1



        #IF DIRECT ACTUATION THEN STORE THE ACTUATION AND SENSING VALUES IN A BUFFER UNTIL THE USER STOPS INTERACTING + 5 SAMPLES
        if in_training == 1:
        	#send direct control to the Processing server instead of prediction
        	client.send_message("/actuator/inflate", act*200-100)

        	#if not started yet, start new buffer for re-training
        	if nr_samples_retrain == 0:



        	nr_samples_retrain += 1
        	#save act to training buffer
        	
	        # plt.scatter(x[i], sX)
	        # plt.scatter(x[i], sY)
	        # plt.scatter(x[i], sZ)
	        #trainXYZ[i]= [sX,sY,sZ]
	        #sinus[i]= [x[i], act]


	        actY[i] = act

        	i+=1

	        if i not in range(len(x)): 
	          break

	    if direct_actuation == 1
	    	in_training = 1
	    	continue

        #IF NO DIRECT ACTUATION WAS GIVEN, THEN USE PREDICTION

        #COMMENT UNTIL HERE IF YOU WANT THIS TO WORK WITHOUT RE-TRAINING
        breathing=model.predict(XYZ)




        print(breathing.shape)
        print(breathing[0][0])
        print(type(breathing[0][0]))

        value = breathing[0][0]*200 - 100

        # if breathing[0][0] <= 1 and breathing[0][0] >= 0:
        client.send_message("/actuator/inflate", value)
        #else:
        	#client.send_message("/actuator/inflate", 0.0)


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
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--ip",
    #                     default="192.168.1.176", help="The ip to listen on")
    # parser.add_argument("--port",
    #                     type=int, default=5006, help="The port to listen on")
    # args = parser.parse_args()
    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/sensor/x", updateX)
    dispatcher.map("/sensor/y", updateY)
    dispatcher.map("/sensor/z", updateZ)

    dispatcher.map("/accxyz", updtouchOSC)

    dispatcher.map("/actuator/1/inflate", updateAct)

    server = osc_server.ThreadingOSCUDPServer(
    ("192.168.0.150", 5006), dispatcher)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()
    if stop():
      server.close()


client = udp_client.SimpleUDPClient("127.0.0.1", 32000)
client.send_message("/actuator/inflate", 0.0)

  # print("Serving on {}".format(server.server_address))
  # server.serve_forever()

thread2 = threading.Thread(target = server)
thread2.start()


calibrateAct()
#calibrateSinus()


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

 