
#https://machinelearningmastery.com/arima-for-time-series-forecasting-with-python/s

import pandas as pa
from matplotlib import pyplot
from pandas.plotting import autocorrelation_plot
from statsmodels.tsa.arima_model import ARIMA
from pandas import DataFrame
from sklearn.metrics import mean_squared_error

from statsmodels.tsa.stattools import adfuller
def test_stationarity(timeseries):
    
    #Determing rolling statistics
    rolmean = timeseries.rolling(100).mean()
    rolstd = timeseries.rolling(100).std()

    #Plot rolling statistics:
    orig = pyplot.plot(timeseries, color='blue',label='Original')
    mean = pyplot.plot(rolmean, color='red', label='Rolling Mean')
    std = pyplot.plot(rolstd, color='black', label = 'Rolling Std')
    pyplot.legend(loc='best')
    pyplot.title('Rolling Mean & Standard Deviation')
    pyplot.show(block=False)
    
    #Perform Dickey-Fuller test:
    print ('Results of Dickey-Fuller Test:')
    dftest = adfuller(timeseries.iloc[:,0].values, autolag='AIC')
    dfoutput = pa.Series(dftest[0:4], index=['Test Statistic','p-value','#Lags Used','Number of Observations Used'])
    for key,value in dftest[4].items():
        dfoutput['Critical Value (%s)'%key] = value
    print (dfoutput)

#get data
def GetData(fileName):
    return pa.read_csv(fileName, header=0, sep="\t", index_col="frame", usecols = ["frame","/actuator/inflate"])

#read time series from the exchange.csv file 
series = GetData('intensity_2P_breathing signal.txt')

#view top 10 records
print(series.head(10))
print(series.dtypes)

# test_stationarity(series)

# print(series.['1':'3'])

# series.plot()
# autocorrelation_plot(series)

X = series.values
size = int(len(X) * 0.75)
train, test = X[0:size], X[size:len(X)]
history = [x for x in train]

# model = ARIMA(train, order=(7,1,0))
# model_fit = model.fit(disp=0)
# forecast = model_fit.predict(len(train),len(train)+400, typ="levels")

# sample=1
# for yhat in forecast:
#     # print('Sample %d: %f' % (sample, forecast))
#     history.append(forecast)
#     sample += 1


predictions = list()

for t in range(len(test)):
    model = ARIMA(history, order=(2,1,0))
    model_fit = model.fit(disp=0)
    output = model_fit.forecast()
    yhat = output[0]
    predictions.append(yhat)
    obs = test[t]
    history.append(obs)
    print('predicted=%f, expected=%f' % (yhat, obs))
error = mean_squared_error(test, predictions)
print('Test MSE: %.3f' % error)
pyplot.plot(test)
pyplot.plot(predictions, color='red')
pyplot.show()

# model = ARIMA(series, order=(5,1,0))
# model_fit = model.fit(disp=0)
# print(model_fit.summary())
# # plot residual errors
# residuals = DataFrame(model_fit.resid)
# residuals.plot()
# pyplot.show()
# residuals.plot(kind='kde')
# pyplot.show()
# print(residuals.describe())

pyplot.show()


