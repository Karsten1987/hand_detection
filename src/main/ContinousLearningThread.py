'''
Created on Dec 2, 2012

@author: karsten
'''
from main.LearningThread import LearningThread
from learning.LeastSquareFilter import LeastSquareFilter
from learning.Interpolator import Interpolator
import pygame
import time
from application.LinuxInputSimulator import MousepointerSimulator

class ContinousLearningThread(LearningThread):

    def __init__(self, trajectoryQueue, sync, stop):
        self.leastSquare = LeastSquareFilter(5)
        self.mousepointer = MousepointerSimulator(None)
        LearningThread.__init__(self, trajectoryQueue, sync, stop)
        
        self.pygame = pygame.init()
        info = pygame.display.Info()
        displayX = info.current_w
        displayY = info.current_h
        scalingX = displayX/400;
        scalingY = displayY/300;
        self.interpolator = Interpolator(scalingX,scalingY)
        
    def run(self):
        while True:
            self.event.wait()
            if self.stop.isSet():
                print 'learning will stop'
                return
            print 'learning goes to run'
            try:
                trajectoryPoint = self.trajectoryQueue.popDataPoint()
                mouseLoc = self.leastSquare.addPoint(trajectoryPoint)  
                if mouseLoc != None:
                    mousLocList = self.interpolator.interpolate(mouseLoc)
                    for loc in mousLocList :
                        self.mousepointer.moveToPoint(loc)
                        time.sleep((1./35)/len(mousLocList))
            except IndexError:
                print 'read from empty queue'
            self.event.clear()
            print 'learning thread goes to sleep'