'''
Created on Dec 1, 2012

@author: karsten
'''
import numpy as np
class TrajectoryPoint(object):

    def __init__(self, ID, location, time, prob, scale=1, orientation=1):
        (x,y) = location
        self.data = [ID,np.array([x,y]), time, prob, scale, orientation]
        
    def getDataArray(self):
        return self.data
    
    def getID(self):
        return self.data[0]
    
    def getLocation(self):
        return self.data[1]
    
    def getTime(self):
        return self.data[2]
    
    def getProb(self):
        return self.data[3]

    
        