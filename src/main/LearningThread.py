'''
Created on Dec 1, 2012

@author: karsten
'''
import threading
import abc

class LearningThread(threading.Thread):
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, trajectoryQueue, sync, stop):
        self.trajectoryQueue = trajectoryQueue
        print 'trajectory ID learning'
        print self.trajectoryQueue
        self.event = sync
        self.stop = stop
        threading.Thread.__init__(self)
        
    @abc.abstractmethod
    def run(self):
        return