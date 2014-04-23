import cv2 as cv2
from vision.VideoWindow import VideoWindow
from vision.InitTemplateMatcher import InitTemplateSearcher
from vision.StartTemplateMatcher import StartTemplateSearcher
import common
from learning.TrajectoryPoint import TrajectoryPoint
import time
import numpy as np
from vision.SkinDetection import SkinDetection

BACKGROUND_TEXT = "press space bar for selecting background"
INIT_TEXT = "select init template"
START_TEXT = "select start template"
APPLICATION_STARTED = 'application started'
INIT_CALIBRATE = "calibrating init foreground"
START_CALIBRATE = "calibrating start foreground"
WINDOW_TITLE = "Video output"

class Handcommands(object):

    def __init__(self, trajectoryQueue):
        self.trajectoryQueue = trajectoryQueue
        
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.cv.CV_CAP_PROP_GAIN,0)
        
        self.initProb = 0
        self.startProb = 0
        self.dummyProb = 0
        
        self.filterWeight = 0.1;
        
        self.crossValidSize = 100
        self.crossValidWeight = 2.0
        
    def __getFrame__(self):
        img = self.capture.read()[1]
        #img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY,dstCn=1)
        #img = cv2.equalizeHist(img)
        #img = cv2.GaussianBlur(img,(3,3),1)
        img = cv2.medianBlur(img, 3)
        return img
    
    def __skipFrames__(self, frameCount, text = None):
        index = 0
        while index<frameCount:
            img = self.__getFrame__()
            if text != None:
                self.video.setText(text)
            self.video.showImg(img)
            cv2.waitKey(1)
            index +=1
        return self.__getFrame__()


    def __extractTemplate(self, text):
        template = None
        while template == None:
            img = self.__getFrame__()
            template = self.video.extractMouseArea(img)
            self.video.setText(text)
            self.video.showImg(img)
            key = cv2.waitKey(1)
            if key == 27:
                self.video.destroyWindow()
                self.capture.release()
                return None
        return template

            
            
    def __extractBackground(self,template,templateMatcher, text):
        n = 50
        maxProb = 0
        for _ in range(n):
            img = self.__getFrame__()
            self.video.setText(text)
            prob,_ = templateMatcher.matchInitTemplate(img, False)
            if prob > maxProb:
                maxProb = prob
            self.video.showImg(img)
            cv2.waitKey(1)
        return maxProb
    

    def __extractForeground(self, template, templateMatcher, text):
        n = 50
        accProb = 0
        for _ in range(n):
            img = self.__getFrame__()
            self.video.setText(text)
            prob,_ = templateMatcher.matchInitTemplate(img, False)
            accProb += prob
            self.video.showImg(img)
            cv2.waitKey(1)
        return accProb/n
    
    
    def startMainLoop(self):
        verbose = False
        self.video = VideoWindow(WINDOW_TITLE)   
        
        ### CONFIGURATION ###
        # Extract init template and threshold
        initTemplate = self.__extractTemplate(INIT_TEXT)
        if initTemplate == None:
            return
        
        # Extract start template and threshold
        startTemplate = self.__extractTemplate(START_TEXT)
        if startTemplate == None:
            return
        
        initSearcherParams = []
        #initSearcherParams.append(InitTemplateSearcher.INIT_MATCHER_SHAPE)
        initSearcherParams.append(InitTemplateSearcher.INIT_MATCHER_COLOR)
        initSearcher = InitTemplateSearcher(initTemplate, initSearcherParams)
        hsvInit = cv2.cvtColor(initTemplate,cv2.COLOR_BGR2HSV)
        skinSearcher = SkinDetection(hsvInit, showSkin= True);

        startSearcherParams = []
        startSearcherParams.append(StartTemplateSearcher.INIT_MATCHER_COLOR)
        startSearcher = StartTemplateSearcher(startTemplate, startTemplate)
        ### START MAIN LOOP ###
        initBackgroundprob = 0
        startBackgroundprob = 0
        started = False
        trajectoryID = 0
        trajectoryStartTime = 0
        initThreshold = 0
        startThreshold = 0
        while True:
            img = self.__getFrame__()
            
            initProb, initLoc = initSearcher.matchInitTemplate(img, verbose)
            
            hsvImg = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
            skinResult = skinSearcher.simpleMatch(hsvImg, wholePictureGiven = True, loc =initLoc, showSkin = True)
#            if initBackgroundprob == 0:
#               print 'background not set'
#            elif initProb > initBackgroundprob*3:
#                print 'background prob:\t'+str(initBackgroundprob)
#                print 'initprob:\t'+str(initProb)

            if initThreshold == 0:
                a=1
                #print 'init not calibrated'
            elif (initProb >= initThreshold*0.9) and skinResult:
                print 'init prob:\t'+str(initProb)
                print 'init thres:\t'+str(initThreshold)
                
                common.playSound('beep-10.wav')
                # not started yet, get it started
                if started == False:
                    started = True
                    trajectoryID = 1
                    trajectoryStartTime = time.time()
                    self.__skipFrames__(5)
                    img = self.__getFrame__()

                else:
                    started = False
                    trajectoryStartTime = time.time()
                    startProb, startLoc = startSearcher.matchInitTemplate(img, verbose)
                    datapoint = TrajectoryPoint(-2,startLoc,time.time()-trajectoryStartTime, startProb)
                    self.trajectoryQueue.pushDataPoint(datapoint)
                    self.__skipFrames__(5)
                    img = self.__getFrame__()
                    
            if started == True:
                startProb, startLoc = startSearcher.matchInitTemplate(img, verbose)
                if startProb >= startThreshold*0.9:
                    self.video.drawTextonImg(img, startLoc, str(startProb))
                    cv2.rectangle(img, startLoc, (startLoc[0]+startTemplate.shape[1], startLoc[1]+startTemplate.shape[0]), (0,255,0))
                    datapoint = TrajectoryPoint(trajectoryID,startLoc,time.time()-trajectoryStartTime, startProb)
                    self.trajectoryQueue.pushDataPoint(datapoint)
                    
            self.video.drawTextonImg(img, initLoc,'skin Match: ' + str(skinResult) +' templateMATCH: ' + str(initProb) )
            cv2.rectangle(img, initLoc, (initLoc[0]+initTemplate.shape[1], initLoc[1]+initTemplate.shape[0]), (255,255,0))
            
            self.video.showImg(img)
            key = cv2.waitKey(1)
            key = key%256
            # init = i = 105
            # start = s = 115
            # background = space = 32
            # print = p = 112
            
            # escape button pressed
            if key == 27:
                self.video.destroyWindow()
                self.capture.release()
                return -1
            # print images
            if key == 112:
                self.video.writeImg(img, "image.jpg")
                self.video.writeImg(initTemplate, "inittemplate.jpg")
                self.video.writeImg(startTemplate, "starttemplate.jpg")
            # calibrate init
            if key == 105:
                initThreshold = self.__extractForeground(initTemplate, initSearcher, INIT_CALIBRATE)
                print 'init threshold:\t'+str(initThreshold)
                self.__skipFrames__(15,APPLICATION_STARTED )
            # calibrate start
            if key == 115:
                startThreshold = self.__extractForeground(startTemplate, startSearcher, START_CALIBRATE)
                print 'start threshold:\t'+str(startThreshold)
                self.__skipFrames__(15)
                