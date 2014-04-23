'''
Created on 04.12.2012

@author: Artur
'''
import numpy as np;
import cv2 as cv2;
class backGroundLearner(object):
    '''
    classdocs
    '''


    def __init__(self, startImg = None):
        self.loop = 1.
        self.alpha = 1;
        self.minAlpha = 0.1;
        if(startImg is None):
            self.startImgSet = False;
        else:
            self.background = np.array(startImg,dtype = np.float32);
            self.startImgSet = True;
        '''
        Constructor
        '''
        
    def learnPicture(self,img):
        if(self.startImgSet):
            weight = self.giveAlpha();
            cv2.accumulateWeighted(img, self.background, weight);
        else:
            self.background = np.array(img,dtype = np.float32);
            self.startImgSet = True;
    
    def giveBackground(self):
        showableBackground = np.array(self.background,dtype = np.uint8)
        cv2.imshow('Background', showableBackground)
        return showableBackground
    
    def resetBackground(self):
        self.loop = 1;
        self.alpha = 0;
        self.startImgSet = False;
        
    def giveAlpha(self):
        if(self.alpha == self.minAlpha):
            value = self.minAlpha
        elif(self.alpha < self.minAlpha):
            self.alpha = self.minAlpha;
            value = self.minAlpha
        elif(self.alpha > self.minAlpha):
            self.alpha = 1/self.loop
            value = self.alpha
            self.loop += 1
        return value