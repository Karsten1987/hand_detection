'''
Created on 08.12.2012

@author: Artur
'''
import math

class Interpolator(object):

    def __init__(self,scalingFactorX = 1,scalingFactorY = 1, maximalNumberOfInterPoints = 10, resolution = 1):
        self.maxInterPt = maximalNumberOfInterPoints;
        self.resolution = resolution;
        self.lastPoint = None
        self.scalingX = scalingFactorX;
        self.scalingY = scalingFactorY;
        
    
    def interpolate(self,point):
        point = [point[0]*self.scalingX,point[1]*self.scalingY]
        if(self.lastPoint != None):
            distance = math.sqrt(0. + (self.lastPoint[0] - point[0])**2 + (self.lastPoint[1] - point[1])**2)  
            if (distance/self.resolution >= self.maxInterPt - 1):
                resolution = distance/(self.maxInterPt -1)
            else:
                resolution = self.resolution
            directionVec = [(point[0]-self.lastPoint[0])* resolution/distance,(point[1]-self.lastPoint[1])*resolution/distance]
            interPoints = [None]*int(distance/resolution)
            actPoint = self.lastPoint;
            for i in range(int(distance/resolution)):
                actPoint = [int(self.lastPoint[0] + directionVec[0]*i),int(self.lastPoint[1] + directionVec[1]*i)]
                interPoints[i] = actPoint;
            self.lastPoint = point;
            interPoints.append(point)
            return interPoints
        else:
            self.lastPoint = point
            return [point]