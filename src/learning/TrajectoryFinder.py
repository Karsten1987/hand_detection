'''
Created on 01.12.2012

@author: Artur
'''
import numpy as np;
import matplotlib.pyplot as plt

class FindCorrespondingTrajectories(object):

    def __init__(self,binLevel, draw = False):
        self.learnedTrajectories = []
        self.directionGaussArrayArray = [];
        self.binLevel = binLevel;
        self.learnedTrajectories = 0;
        self.draw = draw;
    '''
    Trajectory pattern
    [ xo    x1    x2...]
    [ y0    y1    y2...]
    [t0    t1     t2...]
        '''
    def learnTrajectory(self,trajectories,trajecId):
        featuredTrajectories = [];
        gaussOfDirectionArray = [];
        for trajectory in trajectories:
            featuredTrajectories.append(Trajectory(trajectory,self.binLevel))
        gaussOfDirectionArray = self.learnDirectionOfTrajectories(featuredTrajectories);
        self.directionGaussArrayArray.append([trajecId,gaussOfDirectionArray])
        self.learnedTrajectories +=1;
        
    def findCorrespondenceOverDirection(self,trajectory):
        featuredTrajec = Trajectory(trajectory,self.binLevel);
        if(self.draw):
            featuredTrajec.drawTrajectory()
            plt.show()
        maxLikelyId = self.directionGaussArrayArray[0][0];
        maxLikely = -np.inf
#        maxLikely = self.directionGaussArrayArray[0][1][0].giveLikely(featuredTrajec.directionFeature[0])
        actualHistogramDepth = 0;
        for trajectoryNumber in range(self.learnedTrajectories):
            likelyList = []
            likely = 0;
            for histogramDepth in range(len(featuredTrajec.directionFeature)):
                actualHistogramDepth = histogramDepth
                likelyList.append(self.directionGaussArrayArray[trajectoryNumber][1][actualHistogramDepth].giveLikely(featuredTrajec.directionFeature[actualHistogramDepth]))
            if(len(featuredTrajec.directionFeature) > 3):
                maxOutlier = max(likelyList)
                maxOutPos = likelyList.index(maxOutlier)
                minOutlier = min(likelyList)
                minOutPos = likelyList.index(minOutlier);
                likelyList[maxOutPos] = 0;
                likelyList[minOutPos] = 0;
            for value in likelyList:
                likely += value
                    
            print('likelyHood for Id:' +str(self.directionGaussArrayArray[trajectoryNumber][0]) +' is ' + str(likely))
            if(likely > maxLikely):
                maxLikely = likely
                maxLikelyId = self.directionGaussArrayArray[trajectoryNumber][0]
#            actualHistogramDepth += 1;
        return maxLikelyId
        
    
    def learnDirectionOfTrajectories(self,featuredTrajectories):
        gaussArray = [];
        
        for histogramLevel in range(self.binLevel):
            mean = 0 * featuredTrajectories[0].directionFeature[histogramLevel];
            covariance = 0 * featuredTrajectories[0].directionFeature[histogramLevel];
            for trajectory in featuredTrajectories:
                mean = mean + trajectory.directionFeature[histogramLevel];
            mean = mean/len(featuredTrajectories)
            
            for trajectory in featuredTrajectories:
                covariance = covariance + (mean-trajectory.directionFeature[histogramLevel])*(mean-trajectory.directionFeature[histogramLevel])
            covariance = covariance/len(featuredTrajectories)
            covariance[covariance == 0] = np.inf;
            covariance[np.isinf(covariance)] = np.min(covariance)*0.25;
            gaussArray.append(normalDistribution(mean,covariance))
        return gaussArray
        
class Trajectory(object):
    def __init__(self,trajectory,binLevel):
        self.trajectory = trajectory;
        self.directionFeature = self.estimateDirectionFeature(trajectory,binLevel)
        
    def estimateDirectionFeature(self,trajectory,histogramAmount):
        directions = self.estimateDirections(trajectory);
        histArray = [];
        binNumber = 2
        offset = 0;
        for i in range(histogramAmount):
            j = i+1
            if(j%2 == 1 and (j > 1)):
                binNumber += 1;
            if(j%2 == 1):
                offset = 0;
            elif(j%2 == 0):
                offset = np.pi/binNumber
                
            histArray.append(self.makeHistogram(directions, binNumber, offset))
        return histArray
    
    def makeHistogram(self,values,binNumber, offset):
        step = 2*np.pi/binNumber
        bins = np.arange(binNumber+1);
        bins = bins *step - np.pi + offset;
        values[values < (offset - np.pi)] += 2 * np.pi 
        hist,edges = np.histogram(values, bins, density = True);
#        noise = np.ones(hist.shape)*0.0005*np.abs(np.random.random())
#        hist = hist + noise;
#        hist = hist/(1+np.sum(noise))
        return hist        
    
    def estimateDirections(self,trajectory):
#        print trajectory.shape
        path = trajectory[0:2,:]
        length = path.shape[1];
        diffPath = path[:,2:length] - path[:,1:length-1];
        directions = np.arctan2(diffPath[1,:],diffPath[0,:]);
        return directions;
    
    def drawTrajectory(self):
        plt.figure()
        plt.plot(self.trajectory[0,:],self.trajectory[1,:])

class normalDistribution(object):
    def __init__(self,mean,covariance):
        self.mean = mean;
        self.invCovariance = 1/covariance;
        self.logNormalizer = np.sum(np.log(1/np.sqrt(2*np.pi)*np.sqrt(self.invCovariance)))
    
    def giveLikely(self,x):
        likely = np.sum(-0.5*(x-self.mean)*self.invCovariance*(x-self.mean)) + self.logNormalizer
        return likely
    
