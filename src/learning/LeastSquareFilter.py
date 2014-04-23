'''
Created on 01.12.2012

@author: Artur
'''
import numpy as np

class LeastSquareFilter(object):
    def __init__(self,numberOfRespectedPoints):
        self.amount =  numberOfRespectedPoints
        self.positionMatrix = np.array(np.ones((2,numberOfRespectedPoints)))
        self.timeLine = np.array(np.ones((1,numberOfRespectedPoints)))
        self.startFilter = False
        self.counter = 0
    
    def incrementCounter(self):
        if(self.counter >= self.amount-1):
            self.counter = 0
        else:
            self.counter += 1
    
    def addPoint(self,noisyPoint):
        self.positionMatrix[:,self.counter] = noisyPoint.getLocation()
        self.timeLine[:,self.counter] = noisyPoint.getTime()
        self.incrementCounter()
        if((not self.startFilter) and (self.counter == 0)):
            self.startFilter = True
        if(self.startFilter):
            output = self.filter(noisyPoint.getTime())
            return self.sendOutput(output)
    
    def filter(self,time):
        a = np.transpose(np.vstack((np.ones((1,self.amount)),self.timeLine)))
        w = np.linalg.lstsq(a, b = np.transpose(self.positionMatrix), rcond = -1)[0]
        x = np.dot(np.array([1,time]),w) 
        return(x)
    
    def sendOutput(self, output):
        print('estimation:' + str(output))
        return output