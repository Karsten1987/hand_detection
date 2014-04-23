'''
Created on Dec 2, 2012

@author: karsten
'''
from main.LearningThread import LearningThread
from learning.TrajectoryFinder import FindCorrespondingTrajectories
import numpy as np
from application.DbusAudacious import Audacious
from sys import platform
from application.LinuxInputSimulator import KeystrokeSimulator

class BinaryLearningThread(LearningThread):

    '''
    trajectory dict:
    #1 Up/Down
    #2 to the right
    '''
    def __init__(self, trajectoryQueue, sync, stop, dumpTrajectories):
        self.trajectoryFinder = FindCorrespondingTrajectories(8,False)
        self.dumpTrajectories = dumpTrajectories
        self.filePath = 'trajectories.csv'
        
        ''' use adacious as example application
            make artificial circle trajectories. Debug purpose only'''
        if platform == 'linux' or platform == 'linux2':
            self.audacious = Audacious()
            self.keystroke = KeystrokeSimulator()
        #self.__getDebugCircleData()
        self.__setTrajectoryData()
        LearningThread.__init__(self, trajectoryQueue, sync, stop)
        
    def dumpData(self, npTraj):
        f = open(self.filePath, 'a')
        separater = ','
        dataString= ''
        for row in npTraj:
            rowString = ''
            for entry in row:
                rowString += str(entry)+separater
            dataString += rowString+'\n'
        print dataString
        f.write(dataString)
    
    def run(self):
        trajectory = []
        while True:
            
            self.event.wait()
            if self.stop.isSet():
                print 'learning will stop'
                return
            try:
                trajectoryPoint = self.trajectoryQueue.popDataPoint()
                ID =trajectoryPoint.getID()
                if  ID == -1:
                    ID = trajectoryPoint.getID()
                    trajectory = []
                elif ID == -2:
                    npTraj = np.transpose(np.array(trajectory))
                    if self.dumpTrajectories:
                        self.dumpData(npTraj)
                    print 'trajectory will be sent'
                    foundId = self.trajectoryFinder.findCorrespondenceOverDirection(npTraj) 
                    print "found traj id:\t"+str(foundId)
                    
                    self.doAction(foundId)
                    trajectory = []
                else:
                    loc = trajectoryPoint.getLocation()
                    trajectory.append([loc[0], loc[1], trajectoryPoint.getTime()])
            except IndexError:
                print 'read from empty queue'
            self.event.clear()
#            print 'learning thread goes to sleep'
            
    def doAction(self, foundId):
        if self.audacious != None:
            if foundId == 1:
                self.audacious.pause()
            if foundId == 2:
                self.audacious.play_next()
        if self.keystroke != None:
            if foundId == 2:
                self.keystroke.sendKey()
        print('action')
            
            
    def __readFileData(self, filepath):
        trajectories = []
        f1 = open(filepath, 'r')
        counter = 0
        trajectory = []
        for line in f1:
            counter +=1
            values = np.fromstring(line, dtype=np.float64, sep=',')
            trajectory.append(values)
            if counter%3==0:
                trajectories.append(np.array(trajectory))
                trajectory = []
        return trajectories
    
    def __setTrajectoryData(self):
        trajectory1 = self.__readFileData('trajectories_1.csv')
        self.trajectoryFinder.learnTrajectory(trajectory1, 1)
        trajectory2 = self.__readFileData('trajectories_2.csv')
        self.trajectoryFinder.learnTrajectory(trajectory2, 2)        
        
        
        
    #########################################################
    #########################################################
    #########################################################
    def corruptAndCopy(self, noiseRate,copyNumber,trajectory):
        corruptedTrajectory = [];
        for i in range(copyNumber):
            corrupted = np.copy(trajectory);
            noise = noiseRate*np.vstack((np.random.randn(corrupted.shape[1]),np.random.randn(corrupted.shape[1])))
            corrupted[0:2,:] = corrupted[0:2,:] + noise
            corruptedTrajectory.append(corrupted)
        return corruptedTrajectory;
        
    def makeCircle(self, w,time):
        x = np.cos(w*time);
        y = np.sin(w*time);
        return np.vstack((x,y,time))

    def makeLine(self,theta,velocity,time):
        x = np.cos(theta)*velocity*time;
        y = np.sin(theta)*velocity*time;
        return np.vstack((x,y,time))

    def makeWave(self,v,w,time):
        x = v*time;
        y = np.sin(w*time);
        return np.vstack((x,y,time))
    
    def __getDebugCircleData(self):
        noiseRate = 0.001;
        T = 3;
        resolution = 1./30;
        steps = T/resolution;
        time = np.linspace(0, T, steps);
        
        
        ####### Generate Training-data and train ##########################
        k = 5
#        line = self.makeLine(180./180*np.pi,1./T,time)
#        corLines = self.corruptAndCopy(noiseRate,k,line)
#        self.trajectoryFinder.learnTrajectory(corLines, 1)
##        
#        line = self.makeLine(0./180*np.pi,1./T,time)
#        corLines = self.corruptAndCopy(noiseRate,k,line)
#        self.trajectoryFinder.learnTrajectory(corLines, 2)
        
        line = self.makeCircle(2*np.pi/T,time)
        corLines = self.corruptAndCopy(noiseRate,k,line)
        self.trajectoryFinder.learnTrajectory(corLines, 3)
        
        line = self.makeWave(1./T,2*np.pi,time)
        corLines = self.corruptAndCopy(noiseRate,k,line)
        self.trajectoryFinder.learnTrajectory(corLines, 4)
        
