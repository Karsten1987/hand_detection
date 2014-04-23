'''
Created on Nov 16, 2012

@author: karsten
'''
from learning.TrajectoryQueue import TrajectoryQueue
from main.VisionThread import VisionThread
import threading
from main.BinaryLearningThread import BinaryLearningThread
from main.ContinousLearningThread import ContinousLearningThread
import sys

MODE_CONTINOUS = 'continous'
MODE_BINARY = 'binary'

if __name__ == '__main__':
    
    mode = MODE_BINARY
    
    trajectoryQueue = TrajectoryQueue()
    
    sync = threading.Event()
    sync.clear()
    
    stop = threading.Event()
    stop.clear()
    
    visionThread = VisionThread(trajectoryQueue)
    visionThread.setDaemon(True)
    
    if mode == MODE_BINARY:
        learningThread = BinaryLearningThread(trajectoryQueue, sync, stop, False)
    elif mode == MODE_CONTINOUS:
        learningThread = ContinousLearningThread(trajectoryQueue, sync, stop)
    else:
        print 'no valid mode set'
        sys.exit(1)
    
    visionThread.start()
    learningThread.start()
    
    while visionThread.is_alive():
        if trajectoryQueue.getLength()==0:
            sync.clear()
        else:
            sync.set()
    
    stop.set()
    sync.set()
        