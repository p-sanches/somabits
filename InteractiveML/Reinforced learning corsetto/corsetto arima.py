"""

This version of the corset tries to implement a linear model for learning a breathing signal and translating to an actuator signal

It receives two inputs: 1) respiratory signal, and 2) direct actuation 

It outputs one thing: 1) volume of inflation

Let's do this sequentially:
The simplest version will simply translate respiratory signal to volume of inflation via two steps: 1) ARIMA and 2) a transfer function

The next step will be to add direct actuation, by making the model multivariate


Sources to read: https://towardsdatascience.com/3-facts-about-time-series-forecasting-that-surprise-experienced-machine-learning-practitioners-69c18ee89387
http://ismm.ircam.fr/wp-content/uploads/2017/08/BITalino-R-IoT-Programming-Flashing-Guide-v1.1.pdf


Riot with FSR has id 1
Riot with breathing has id 0
Same arg for both = 12


"""
import argparse
import math
import time
import threading
#from input_buffer import InputBuffer
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
# from keras.preprocessing.sequence import TimeseriesGenerator
# from keras.models import Sequential
# from keras.layers import Dense
# from keras.layers import MaxPooling1D
# from keras.layers import Conv1D
# from keras.layers import Flatten
# from keras.layers import LSTM

from statsmodels.tsa.arima_model import ARIMA

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
# from keras.models import load_model


from pythonosc import osc_message_builder
from pythonosc import udp_client

import sched, time

BITALINO_RIOT_BREATHING = "/0/raw"
BITALINO_RIOT_FSR = "/1/raw"
RIOT_A1_ARG = 12 #this is the arg number of the riot that pavel connected to a breathing sensor at A1


SECONDS_TO_SLEEP = 0.2

IPAddressListener = "192.168.1.5"
PortListener = 5006

IPAddressActuator = "127.0.0.1"
PortActuator = 12345

resp=0
press=0

breathing = 0



def print_volume_handler(unused_addr, args, volume):
  print("[{0}] ~ {1}".format(args[0], volume))

def print_compute_handler(unused_addr, args, volume):
  try:
    print("[{0}] ~ {1}".format(args[0], args[1](volume)))
  except ValueError: pass

#get data
def GetSampleOutData():
    return pa.read_csv("output1561706008144.txt", header=0, sep="\t", usecols = ["/actuator/inflate"])

def respUpd(address, *args):
  
  
  global resp
  resp=args[0] #http://ismm.ircam.fr/wp-content/uploads/2017/08/BITalino-R-IoT-Programming-Flashing-Guide-v1.1.pdf 
  #print(resp)	

def pressureUpd(address, *args):
  #print("pressure input")
  
  global press
  press=args[0]
  print(press)


def listener():
    from pythonosc import dispatcher
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--ip",
    #                     default="192.168.1.176", help="The ip to listen on")
    # parser.add_argument("--port",
    #                     type=int, default=5006, help="The port to listen on")
    # args = parser.parse_args()

    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/sensor/z", respUpd)
    dispatcher.map("/pressure", pressureUpd)

    server = osc_server.ThreadingOSCUDPServer(
    (IPAddressListener, PortListener), dispatcher)
    print("Listening on {}".format(server.server_address))
    server.serve_forever()
    if stop():
      server.close()


# client = udp_client.SimpleUDPClient(IPAddressActuator, PortActuator)
# client.send_message("/radius", 20.0)

  # print("Serving on {}".format(server.server_address))
  # server.serve_forever()

threadListener = threading.Thread(target = listener)
threadListener.start()


starttime=time.time()

MIN_SAMPLES = 20
samplenr = 0
sample_buffer = []

prediction  = 0


while True:

  time.sleep(SECONDS_TO_SLEEP - ((time.time() - starttime) % SECONDS_TO_SLEEP))
  print ("tick")

  #initializing phase, just to get a few samples before we start making predictions
  if samplenr < MIN_SAMPLES: 
  	print ("INITIAL PHASE:", resp)

  	sample_buffer.append(resp)
  	samplenr += 1
  	continue

  print("Prediction=", prediction)
  print("Actual=", resp)
  print("Difference=", prediction-resp)

  #after initializing phase, start making predictions
  model = ARIMA(sample_buffer, order=(5,1,0))
  model_fit = model.fit(disp=0)
  output = model_fit.forecast()
  prediction = output[0]
  sample_buffer.append(resp)


  #transfer function from respiration to volume

  samplenr += 1
  




# thread1 = threading.Thread(target = get_breathing)
# thread1.start()


# calibrate()
# thread2.join()
# print("Stopped listening to OSC commands. Plz stop sending them")

# plt.set_ylim([-1,1])
# plt.plot(y, color="black")
# plt.plot(sensorX, color="red")
# plt.plot(sensorY, color="green")
# plt.plot(sensorZ, color="blue")
# plt.show()

 