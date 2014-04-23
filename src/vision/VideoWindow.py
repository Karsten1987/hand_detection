'''
Created on Dec 3, 2012

@author: karsten
'''
import cv2 as cv2
from vision import common

class VideoWindow(object):

    def __init__(self, windowName):
        self.windowName = windowName
        cv2.namedWindow(self.windowName)
        cv2.setMouseCallback(self.windowName, self.onmouse)
        
        self.drawingLocation = (50,50)
        
        self.start = None
        self.started = False
        self.end = None
        self.ended = None
        
    def destroyWindow(self):
        cv2.destroyWindow(self.windowName)
        
    def setText(self, text):
        self.drawText = text
        
    def onmouse(self, sync, x, y, flags, param):
        if sync == cv2.EVENT_LBUTTONDOWN:
            self.start = (x,y)
            self.started = True
            self.ended = False
        if sync == cv2.EVENT_MOUSEMOVE and self.started==True:
            self.end = (x,y)
        if sync == cv2.EVENT_LBUTTONUP and self.started==True:
            self.started = False
            self.ended = True
            self.end = (x,y)
            
    def extractMouseArea(self, img):
        template = None
        if self.started:
            cv2.rectangle(img, self.start, self.end, (255,0,0))
        if self.ended == True:
            template = img[self.start[1]:self.end[1], self.start[0]: self.end[0]]
            self.ended = False
            self.started = False
        return template
            
    def showImg(self, img):
        common.draw_str(img, self.drawingLocation, self.drawText)
        cv2.imshow(self.windowName, img)
        
    def drawTextonImg(self, img, loc, text):
        common.draw_str(img, loc, text)
        
    def writeImg(self, img, filename):
        cv2.imwrite(filename, img)
        
        