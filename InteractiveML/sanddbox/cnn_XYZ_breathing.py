#On why cnn vs rnn https://medium.com/@alexrachnog/deep-learning-the-final-frontier-for-signal-processing-and-time-series-analysis-734307167ad6
#https://www.dlology.com/blog/how-to-use-keras-timeseriesgenerator-for-time-series-data/
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
    return pa.read_csv(fileName, header=0, sep="\t", usecols = ["1/gravity/x","1/gravity/y","1/gravity/z"])

#get data
def GetOutData(fileName):
    return pa.read_csv(fileName, header=0, sep="\t", usecols = ["/actuator/inflate"])

def delta_time_series(data):
    return data[1:]- data[:-1]


def plot_delta(data):
    plt.plot(delta_time_series(data))
    plt.ylabel('close')
    plt.show()    

def get_y_from_generator(gen):
    '''
    Get all targets y from a TimeseriesGenerator instance.
    '''
    y = None
    for i in range(len(gen)):
        batch_y = gen[i][1]
        if y is None:
            y = batch_y
        else:
            y = np.append(y, batch_y)
    y = y.reshape((-1,1))
    print(y.shape)
    return y

def binary_accuracy(a, b):
    '''
    Helper function to compute the match score of two 
    binary numpy arrays.
    '''
    assert len(a) == len(b)
    return (a == b).sum() / len(a)

#read time series from the exchange.csv file 
seriesIn = GetInData('output1561706008144.txt')
seriesOut = GetOutData('output1561706008144.txt')

# dataset_delta = delta_time_series(series)
# plot_delta(series)
# plt.plot(series)
# plt.show()

# print(series.shape)

# dataset = dataset_delta
datasetIn=seriesIn
datasetOut=seriesOut


# normalize the dataset
scaler = MinMaxScaler(feature_range=(0, 1))
datasetIn = scaler.fit_transform(datasetIn)
datasetOut = scaler.fit_transform(datasetOut)

# split into train and test sets
train_size = int(len(datasetIn) * 0.40)
test_size = len(datasetIn) - train_size

trainIn, testIn = datasetIn[0:train_size,:], datasetIn[train_size:len(datasetIn),:]

trainOut, testOut = datasetOut[0:train_size,:], datasetOut[train_size:len(datasetOut),:]

look_back = 20 #frame rate of processing = 60;
n_features=3

#FIRST CNN to fit shape of actuator
# train_data_gen1 = TimeseriesGenerator(trainOut, trainOut,
#                                length=look_back, sampling_rate=1,stride=1,
#                                batch_size=3)

# test_data_gen1 = TimeseriesGenerator(testOut, testOut,
#                                length=look_back, sampling_rate=1,stride=1,
#                                batch_size=1) 

# model1 = Sequential()
# # model1.add(Flatten())
# model1.add(Conv1D(filters=64, kernel_size=2, activation='relu', input_shape=(look_back, n_features)))
# model1.add(MaxPooling1D(pool_size=2))
# model1.add(Flatten())
# model1.add(Dense(50, activation='relu'))
# model1.add(Dense(1))
# model1.compile(optimizer='adam', loss='mse')


# history1 = model1.fit_generator(train_data_gen1, epochs=1).history
# model1.save('cnn_actuator_model.h')


# model1 = load_model('cnn_actuator_model.h')

# model1.evaluate_generator(test_data_gen1)

# trainPredict1 = model1.predict_generator(train_data_gen1)
# trainPredict1.shape

# testPredict1 = model1.predict_generator(test_data_gen1)
# testPredict1.shape

# # invert predictions, scale values back to real index/price range.
# trainPredict1 = scaler.inverse_transform(trainPredict1)
# testPredict1 = scaler.inverse_transform(testPredict1)

# trainY1 = get_y_from_generator(train_data_gen1)
# testY1 = get_y_from_generator(test_data_gen1)

# trainY1 = scaler.inverse_transform(trainY1)
# testY1 = scaler.inverse_transform(testY1)

# # calculate root mean squared error
# trainScore = math.sqrt(mean_squared_error(trainY1[:,0], trainPredict1[:,0]))
# print('Train Score: %.2f RMSE' % (trainScore))
# testScore = math.sqrt(mean_squared_error(testY1[:, 0], testPredict1[:,0]))
# print('Test Score: %.2f RMSE' % (testScore))


# datasetOut = scaler.inverse_transform(datasetOut)
# datasetOut.shape

# # shift train predictions for plotting
# trainPredictPlot = np.empty_like(datasetOut)
# trainPredictPlot[:, :] = np.nan
# trainPredictPlot[look_back:len(trainPredict1)+look_back, :] = trainPredict1
# # Delta + previous close
# # trainPredictPlot = trainPredictPlot + series[1:]
# # set empty values
# # trainPredictPlot[0:look_back, :] = np.nan
# # trainPredictPlot[len(trainPredict)+look_back:, :] = np.nan

# # shift test predictions for plotting
# testPredictPlot = np.empty_like(datasetOut)
# testPredictPlot[:, :] = np.nan
# testPredictPlot[len(trainPredict1)+(look_back*2):len(datasetOut), :] = testPredict1

# # Delta + previous close
# # testPredictPlot = testPredictPlot + series[1:]
# # set empty values
# # testPredictPlot[0:len(trainPredict)+(look_back*2), :] = np.nan
# # testPredictPlot[len(dataset):, :] = np.nan

# # plot baseline and predictions
# plt.plot(seriesOut[1:])
# plt.plot(trainPredictPlot)
# plt.plot(testPredictPlot)
# plt.show()


# datasetOut = scaler.fit_transform(datasetOut)

#Second CNN to associate sensor(s) with actuator---------------------------------------------------
train_data_gen = TimeseriesGenerator(trainIn, trainOut,
                               length=look_back, sampling_rate=1,stride=1,
                               batch_size=3)

test_data_gen = TimeseriesGenerator(testIn, testOut,
                               length=look_back, sampling_rate=1,stride=1,
                               batch_size=1) 


                                                          
model = Sequential()
model.add(Conv1D(filters=64, kernel_size=2, activation='relu', input_shape=(look_back, n_features)))
# model.add(Conv1D(filters=64, kernel_size=1, activation='relu', input_shape=(look_back, n_features)))
model.add(MaxPooling1D(pool_size=2))
model.add(Flatten())
model.add(Dense(50, activation='relu'))
model.add(Dense(1))
model.compile(optimizer='adam', loss='mse')

# from keras.utils import plot_model
# plot_model(model, to_file='model.png', show_shapes=True)
# from IPython.display import Image
# Image(filename='model.png')


history = model.fit_generator(train_data_gen, epochs=3).history
model.save('xyz_breathing.h')


model = load_model('xyz_breathing.h')

model.evaluate_generator(test_data_gen)

trainPredict = model.predict_generator(train_data_gen)
trainPredict.shape

testPredict = model.predict_generator(test_data_gen)
testPredict.shape

# invert predictions, scale values back to real index/price range.
trainPredict = scaler.inverse_transform(trainPredict)
testPredict = scaler.inverse_transform(testPredict)

trainY = get_y_from_generator(train_data_gen)
testY = get_y_from_generator(test_data_gen)

trainY = scaler.inverse_transform(trainY)
testY = scaler.inverse_transform(testY)

# calculate root mean squared error
trainScore = math.sqrt(mean_squared_error(trainY[:,0], trainPredict[:,0]))
print('Train Score: %.2f RMSE' % (trainScore))
testScore = math.sqrt(mean_squared_error(testY[:, 0], testPredict[:,0]))
print('Test Score: %.2f RMSE' % (testScore))

datasetIn = scaler.inverse_transform(datasetIn)
datasetIn.shape
datasetOut = scaler.inverse_transform(datasetOut)
datasetOut.shape

# shift train predictions for plotting
trainPredictPlot = np.empty_like(datasetIn)
trainPredictPlot[:, :] = np.nan
trainPredictPlot[look_back:len(trainPredict)+look_back, :] = trainPredict
# Delta + previous close
# trainPredictPlot = trainPredictPlot + series[1:]
# set empty values
# trainPredictPlot[0:look_back, :] = np.nan
# trainPredictPlot[len(trainPredict)+look_back:, :] = np.nan

# shift test predictions for plotting
testPredictPlot = np.empty_like(datasetIn)
testPredictPlot[:, :] = np.nan
testPredictPlot[len(trainPredict)+(look_back*2):len(datasetIn), :] = testPredict

# Delta + previous close
# testPredictPlot = testPredictPlot + series[1:]
# set empty values
# testPredictPlot[0:len(trainPredict)+(look_back*2), :] = np.nan
# testPredictPlot[len(dataset):, :] = np.nan

# plot baseline and predictions
# plt.plot(datasetIn)
plt.plot(seriesOut[1:])
plt.plot(trainPredictPlot)
plt.plot(testPredictPlot)
plt.show()


# df['t'] = series.values[:,0]

#FEED ONE INTO THE OTHER!! Breathing goes in, then result from model1 (actuator) goes out
# model = load_model('cnn_control_model.h')
# model1 = load_model('cnn_actuator_model.h')

# testPredict = model.predict_generator(test_data_gen) # this gives the mapping of breathing to actuator

# #now I need to pass that output through the model that knows the correct shape of the actuator

# testPredict=np.append(np.zeros(30),testPredict )


# final_test_data_gen = TimeseriesGenerator(testPredict, testOut,
#                                length=look_back, sampling_rate=1,stride=1,
#                                batch_size=1) 

# model1.predict_generator(final_test_data_gen)


# testPredict = model1.predict_generator(testPredict)