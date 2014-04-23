'''
Created on 06.12.2012

@author: Artur
'''
import numpy as np
import cv2

class SkinDetection(object):
    '''
    classdocs
    '''


    def __init__(self,rgbTemplate, bins = 3, showSkin = False):
#       
        self.tVec = None;
        self.invSqrtEigVal = None;
        self.alpha = 2 + 2*np.sqrt(2)

#        self.alpha = 9.3
#        self.alpha = 7;
#         self.template = cv2.cvtColor(rgbTemplate,cv2.COLOR_RGB2YUV);
        self.emIterations =3;
        self.delta = 1.1;       
        self.template = rgbTemplate
        self.template = cv2.medianBlur(self.template, 5);
        self.bins = bins
        self. mean = 0;
        self.threshX = [0,0]
        self.threshY = [0,0]
        self.setParameters()
        self.templateContours = self.findContours(rgbTemplate)
        skin = self.giveMorphedSkin(rgbTemplate)
        if(showSkin):
            cv2.imshow('skinTemplate',skin)
        self.skinTemplateForSimpleMatch = skin * 1.0
        self.skinTemplateForSimpleMatch[self.skinTemplateForSimpleMatch == 255] = 1.0
        Area = rgbTemplate.shape[0]*rgbTemplate.shape[1]
        self.threshRec = np.sum(np.sum(self.skinTemplateForSimpleMatch))/Area *0.5
        self.skinTemplateForSimpleMatch[self.skinTemplateForSimpleMatch == 0] = -1.0
        

    def setParameters(self):
        normedTemplate = self.template;
        normedTemplate = cv2.medianBlur(normedTemplate, 5);
#        normedTemplate[:,:,0] = self.template[:,:,0]/self.template[:,:,2]
#        normedTemplate[:,:,1] = self.template[:,:,1]/self.template[:,:,2]
        pixelArray = np.reshape(normedTemplate, (normedTemplate.shape[0]*normedTemplate.shape[1], normedTemplate.shape[2]))
#        hsArray = pixelArray[:,0:2];
        hist,xEdges,yEdges = np.histogram2d(pixelArray[:,0], pixelArray[:,1], self.bins)
        minMax = cv2.minMaxLoc(hist);
        self.mean = np.array([[(xEdges[minMax[3][0]]+xEdges[minMax[3][0]+1])/2.],[(yEdges[minMax[3][1]]+yEdges[minMax[3][1]+1])/2.]])
        self.threshX = [xEdges[minMax[3][0]],xEdges[minMax[3][0]+1]];
        self.threshY = [yEdges[minMax[3][1]],yEdges[minMax[3][1]+1]];
        eigV1 = np.array([[1./(xEdges[minMax[3][0]+1]-xEdges[minMax[3][0]])],[0]])
        eigV2 = np.array([[0],[1./(yEdges[minMax[3][1]+1]-yEdges[minMax[3][1]])]])
        self.invSqrtEigVal = np.hstack((eigV1,eigV2))/8;
        self.tVec = np.array([[1,0],[0,1]])
        self.trainThresholds(self.template)
        
    def findContours(self,rgbTemplate):
        skinPicture = self.giveMorphedSkin(rgbTemplate);
        contours, hierarchy = cv2.findContours(skinPicture,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
#        cv2.drawContours(skinPicture,contours,-1,255,2);
#        contours = cv2.approxPolyDP(contours,0.1*cv2.arcLength(contours,True),True)
        return  contours
    
    def matchSchapes(self,rgbTemplate):
        count = 0;
        contourW = self.findContours(rgbTemplate);
        contourT = self.templateContours;
        method = cv2.cv.CV_CONTOURS_MATCH_I1;
        minResult = 1000000000000;
        averageResult = np.NAN;
        for tCont in contourT:
            area = cv2.contourArea(tCont) 
            if( area > self.template.shape[0]*self.template.shape[1]*0.1):
                for wCont in contourW:
                    area = cv2.contourArea(wCont)
                    if((area > self.template.shape[0]*self.template.shape[1]*0.1)):
                        result = cv2.matchShapes(tCont, wCont ,method ,0)
                        count += 1
                        if(np.isnan(averageResult)):
                            averageResult = 0;
                        averageResult = averageResult*(1-1/count) +  result/count
                        if(minResult > result):
                            minResult = result
        simpleProb = self.simpleMatch(rgbTemplate)
#        print(count)
        return (1-averageResult)*(1+simpleProb)/2
    
    def simpleMatch(self,rgbExtraction,wholePictureGiven = False,loc = None, showSkin = False):
        skinPicture = 1.0* self.giveMorphedSkin(rgbExtraction,wholePictureGiven,loc, showSkin);
        skinPicture[skinPicture == 0] = -1.
        skinPicture[skinPicture == 255] = 1.
        overlap = skinPicture*self.skinTemplateForSimpleMatch;
        inter = np.sum(overlap);
        value = np.sum(inter)
        value = value/(1.*skinPicture.shape[0] * skinPicture.shape[1])
#        return value
        if(value > self.threshRec):
            return True
        else:
            return False
        
    
    def trainThresholds(self,rgbTemplate):
        
        img = rgbTemplate;

#        Area = (self.threshX[1] - self.threshX[0])* (self.threshY[1] - self.threshY[0])
#        density = value/Area
#        img = rgbTemplate
#        img = cv2.medianBlur(img, 3);
##        img[:,:,0] = img[:,:,0]/img[:,:,2]
##        img[:,:,1] = img[:,:,1]/img[:,:,2]
        for t in range(self.emIterations):
            print('threshX: ' + str(self.threshX) + 'threshY: ' + str(self.threshY))
            skinImg = self.giveSkinPicture(rgbTemplate);
            inter = np.sum(skinImg);
            hits = np.sum(inter)/255;
            print('usedPoints: ' +str(hits))
            hImg = np.zeros((img.shape[0], img.shape[1]), dtype = np.float)
            sImg = np.zeros((img.shape[0], img.shape[1]), dtype = np.float)
            hImg[skinImg == 255] = img[skinImg == 255,0]
            sImg[skinImg == 255] = img[skinImg == 255,1]
            
            
            hArray = np.reshape(hImg, (hImg.shape[0]*hImg.shape[1]))
            sArray = np.reshape(sImg, (hImg.shape[0]*sImg.shape[1]))
            
            cleanHArray = hArray[hArray > 0] 
            cleanSArray = sArray[hArray > 0] 
            combinedArray = np.vstack((cleanHArray,cleanSArray))
            self.cov = np.cov(combinedArray)
            if(self.cov.shape != (2,2)):
                print('covariance Estimation went wrong')
             
            eigVal,eigVec = np.linalg.eig(self.cov)
            self.tVec = eigVec.transpose();
            self.invSqrtEigVal = np.sqrt(np.array([[1/eigVal[0],0],[0,1/eigVal[1]]])); 
            
#            hCov = np.sqrt(np.var(cleanHArray));
            if(hits == 0 ):
                hits = 0.00001
            hMean = np.sum(hArray)/hits
#            sCov = np.sqrt(np.var(cleanSArray));
            sMean = np.sum(sArray)/hits
            
#            self.threshX = [hMean-self.delta*hCov,hMean+ self.delta*hCov]
#            self.threshY = [sMean-self.delta*sCov,sMean+ self.delta*sCov]
            self.mean = np.array([[hMean], [sMean]])
#            print('hCov: ' + str(hCov) + ' sCov: ' + str(sCov) + ' mean ' +str(self.mean) )
    
    def giveMorphedSkin(self,rgbTemplate,wholePictureGiven = False,loc = None, showSkin = False):
        skin = self.giveSkinPicture(rgbTemplate,wholePictureGiven,loc);
        st = cv2.getStructuringElement(2, (3, 3))
        cv2.morphologyEx(skin, 1, st, iterations=20)
#        skin = cv2.medianBlur(skin,5)
#        skin = cv2.GaussianBlur(skin, (5,5), 2)
#        cv2.morphologyEx(skin, 2, st, iterations=5)
        if(showSkin):
            cv2.imshow('skinExtraction', skin)
        return skin
    
    def giveSkinPicture(self,rgbTemplate, wholePictureGiven = False,loc = None ):
#        img = cv2.cvtColor(rgbTemplate,cv2.COLOR_RGB2YUV);
        if(wholePictureGiven):
            img = rgbTemplate[loc[1]:loc[1] + self.template.shape[0], loc[0]:loc[0] + self.template.shape[1]]
        elif(not wholePictureGiven):
            img = rgbTemplate
        img = cv2.medianBlur(img, 3);
        imgVec = np.reshape(img[:,:,0:2], (img.shape[0]*img.shape[1],2))
        imgVec = np.transpose(imgVec)
        skinImg = np.zeros((img.shape[0], img.shape[1]), dtype = np.uint8) 
#        for row in range(img.shape[0]):
#            for column in range(img.shape[1]):
#                orientatedX = np.dot(self.invSqrtEigVal,np.dot(self.tVec,(img[row,column,0:2]- self.mean))) 
#                mahaDist = np.dot(orientatedX.transpose(),orientatedX) 
#                if(mahaDist< self.alpha):
#                    skinImg[row,column] = 255
        imgVec = imgVec - self.mean
        imgVecRot = np.dot(self.invSqrtEigVal,np.dot(self.tVec,imgVec));
        mahaDistances = (imgVecRot*imgVecRot).sum(axis = 0);
        mahaDistances = np.array([mahaDistances]).transpose()
        mahaDistances.shape
        
        choosen = np.less(mahaDistances,self.alpha);
        choosen.shape
        choosen = np.array(choosen)

        if(choosen.shape[0] - skinImg.shape[0]*skinImg.shape[1] < 0):
            print(choosen.shape[0] - skinImg.shape[0]*skinImg.shape[1])
        choosen = np.reshape(choosen, skinImg.shape);
        skinImg[choosen] = 255
        return skinImg
