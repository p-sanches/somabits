
#import pandas
import pandas as pa
from matplotlib import pyplot
from pandas.plotting import autocorrelation_plot
from statsmodels.tsa.arima_model import ARIMA
from pandas import DataFrame
from sklearn.metrics import mean_squared_error

from sklearn.metrics import mean_squared_error
from math import sqrt
from matplotlib import pyplot

from statsmodels.tsa.stattools import adfuller

#get data
def GetData(fileName):
    return pa.read_csv(fileName, header=0, sep="\t", index_col="frame", usecols = ["frame","/actuator/inflate"])

#read time series from the exchange.csv file 
series = GetData('intensity_2P_breathing signal.txt')

#view top 10 records
print(series.head(10))
print(series.dtypes)


X = series.values
size = int(len(X) * 0.75)
train, test = X[0:size], X[size:len(X)]
# walk-forward validation
history = [x for x in train]
predictions = list()
for i in range(len(test)):
    # make prediction
    predictions.append(history[-1])
    # observation
    history.append(test[i])
# report performance
rmse = sqrt(mean_squared_error(test, predictions))
print('RMSE: %.3f' % rmse)
# line plot of observed vs predicted
pyplot.plot(test)
pyplot.plot(predictions)
pyplot.show()
