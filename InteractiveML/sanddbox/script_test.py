
#import pandas
import pandas as pa
from matplotlib import pyplot

#get data
def GetData(fileName):
    return pa.read_csv(fileName, header=0, sep="\t")

#read time series from the exchange.csv file 
exchangeRatesSeries = GetData('intensity_2P_breathing signal.txt')

#view top 10 records
print(exchangeRatesSeries.head(10))

exchangeRatesSeries.plot()
pyplot.show()