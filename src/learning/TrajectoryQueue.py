'''
Created on Dec 1, 2012

@author: karsten
'''

from collections import deque

class TrajectoryQueue():
    def __init__(self):
        self.queue = deque()
        
    def pushDataPoint(self, datapoint):
        self.queue.appendleft(datapoint)
        
    def popDataPoint(self):
        return self.queue.pop()
    
    def getLength(self):
        return len(self.queue)
    
    