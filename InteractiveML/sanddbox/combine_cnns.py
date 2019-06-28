import pandas as pa
from matplotlib import pyplot
import numpy as np
import matplotlib.pyplot as plt
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

#get data
def GetInData(fileName):
    return pa.read_csv(fileName, header=0, sep="\t", usecols = ["1/gravity/x"])

#get data
def GetOutData(fileName):
    return pa.read_csv(fileName, header=0, sep="\t", usecols = ["/actuator/inflate"])



seriesIn = GetInData('output1561706008144.txt')
seriesOut = GetOutData('output1561706008144.txt')


# dataset = dataset_delta
datasetIn=seriesIn
datasetOut=seriesOut


# normalize the dataset
scaler = MinMaxScaler(feature_range=(0, 1))
datasetIn = scaler.fit_transform(datasetIn)
datasetOut = scaler.fit_transform(datasetOut)

# split into train and test sets
train_size = int(len(datasetIn) * 0.00)
test_size = len(datasetIn) - train_size

trainIn, testIn = datasetIn[0:train_size,:], datasetIn[train_size:len(datasetIn),:]

trainOut, testOut = datasetOut[0:train_size,:], datasetOut[train_size:len(datasetOut),:]

look_back = 30 #frame rate of processing = 60; so this means that it looks back 1/2 of a second
n_features=1


#FEED ONE INTO THE OTHER!! Breathing goes in, then result from model1 (actuator) goes out
model = load_model('cnn_control_model.h')
model1 = load_model('cnn_actuator_model.h')


test_data_gen = TimeseriesGenerator(testIn, testOut,
                               length=look_back, sampling_rate=1,stride=1,
                               batch_size=1) 

testPredict = model.predict_generator(test_data_gen) # this gives the mapping of breathing to actuator

#now I need to pass that output through the model that knows the correct shape of the actuator

testPredict=np.append(np.zeros(look_back),testPredict)

testPredict = np.expand_dims(testPredict, axis=2) # reshape (569, 30) to (569, 30, 1) 


final_test_data_gen = TimeseriesGenerator(testPredict, testOut,
                               length=look_back, sampling_rate=1,stride=1,
                               batch_size=1) 

finalTestPredict= model1.predict_generator(final_test_data_gen)

# q = model.predict( np.array( [0,10,0] )  )



# invert predictions, scale values back to real index/price range.
finalTestPredict = scaler.inverse_transform(finalTestPredict)
testPredict = scaler.inverse_transform(testPredict)

plt.plot(seriesOut[1:])
plt.plot(finalTestPredict, color="red")
plt.plot(testPredict, color="green")
plt.show()