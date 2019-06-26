import numpy as np
from matplotlib import pyplot
from scipy.spatial.distance import euclidean

from fastdtw import fastdtw

x = np.array([[1,1], [2,2], [3,3], [4,4], [5,5]])
y = np.array([[2,2], [3,3], [4,4]])

pyplot.plot(x, color='red', label='x')
pyplot.plot(y, color='black', label = 'y')

distance, path = fastdtw(x, y, dist=euclidean)

pyplot.plot(path, color='yellow', label='path')
print(distance)
print(path)
print(x)
pyplot.show()