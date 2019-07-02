#Class that implements a rolling buffer
from scipy.ndimage.interpolation import shift
import numpy as np

class InputBuffer:

    cur=0
    full = False

    """ class that implements a not-yet-full buffer """
    def __init__(self,size_max, n_features):
        self.max = size_max
        self.data = np.zeros((size_max,n_features))
        self.cur=0

   
    def repeated(self,array):
        return np.array_equal(self.data,array)

    def append(self,x,y,z):
        """append an element at the end of the buffer"""
        
        if self.cur == self.max-1:
            self.data=np.roll(self.data, -1, axis=0)
            self.data[self.cur]=[x,y,z]
            self.full=True
        else: 
            self.data[self.cur]=[x,y,z]
            self.cur += 1 

    def get(self):
        """ Return a list of elements from the oldest to the newest. """
        return self.data

    def isFull(self):
        """ Return a list of elements from the oldest to the newest. """
        return self.full