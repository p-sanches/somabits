"""Small example OSC server

This program listens to several addresses, and prints some information about
received packets.
"""
import argparse
import math
import time


from pythonosc import dispatcher
from pythonosc import osc_server
import asyncio

import numpy as np
import matplotlib.pyplot as plt

Fs = 125
f = 1
sample = 100
x = np.arange(sample)
y = np.sin(2 * np.pi * f * x / Fs)

sensorX = np.array(sample)
sensorY = np.array(sample)
sensorZ = np.array(sample)

sX=0
sY=0
sZ=0
server=None

def print_volume_handler(unused_addr, args, volume):
  print("[{0}] ~ {1}".format(args[0], volume))

def print_compute_handler(unused_addr, args, volume):
  try:
    print("[{0}] ~ {1}".format(args[0], args[1](volume)))
  except ValueError: pass

def updateX(address, *args):
  print(args)
  sX=args

def updateY(address, *args):
  print(args)
  sY=args

def updateZ(address, *args):
  print(args)
  sZ=args

def calibrate():

    time.sleep(1)
    for i in range(len(y)):
        plt.scatter(x[i], y[i])
        np.append(sensorX, sX)
        np.append(sensorY, sY)
        np.append(sensorZ, sZ)
        plt.pause(0.01)
    plt.show()

def server():
  print("Serving on {}".format(server.server_address))
  server.serve_forever()

if __name__ == "__main__":
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

  import threading
  thread1 = threading.Thread(target = calibrate)
  thread1.start()

  # print("Serving on {}".format(server.server_address))
  # server.serve_forever()

  thread2 = threading.Thread(target = server)
  thread2.start()



  plt.set_ylim([-1,1])
  plt.plot(y, color="black")
  plt.plot(sensorX, color="red")
  plt.plot(sensorY, color="green")
  plt.plot(sensorZ, color="blue")
  plt.show()

 