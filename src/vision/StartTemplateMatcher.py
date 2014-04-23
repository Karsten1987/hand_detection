'''
Created on Dec 6, 2012

@author: karsten
'''
import cv2 as cv2
import numpy as np

class Matcher(object):
    def __init__(self, template):
        self.template = template
        self.template_width = template.shape[1]
        self.template_height = template.shape[0]

class ShapeMatcher(Matcher):
    def __init__(self, template):
        Matcher.__init__(self, template)
        
    def match(self, img, loc):
        print 'not impelemented yet - shapematcher.match'
        return None, None

class TemplateMatcher(Matcher):
    def __init__(self, template):
        Matcher.__init__(self, template)
        
    def _match(self, img):
        result = cv2.matchTemplate(img, self.template, cv2.TM_CCOEFF_NORMED)
        minmax = cv2.minMaxLoc(result)
        prob = minmax[1]
        loc = minmax[3]
        return prob, loc, result
    
    
class ColorMatcher(TemplateMatcher):
    def __init__(self, template):
        self.offset = 0
        template = cv2.cvtColor(template, cv2.COLOR_BGR2HSV)
        print 'orignal template'
        print template.dtype
        template = np.array(template[:,:,0:2], dtype=np.uint8)
        print 'template shape'
        print type(template)
        Matcher.__init__(self, template)
        
    def match(self, img, (x,y)):
        imgcut = img.copy()
        imgcut = cv2.cvtColor(imgcut, cv2.COLOR_BGR2HSV)
        imgcut = np.array(imgcut[:,:,0:2], dtype=np.uint8)
        imgcut= imgcut[y-self.offset:(y+self.template_height+self.offset),x:(x-self.offset+self.template_width+self.offset)]
        prob, loc,_ = super(ColorMatcher, self)._match(imgcut)
        return prob, loc
        
class GrayMatcher(TemplateMatcher):
    def __init__(self, template):
        grayTemplate = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        Matcher.__init__(self, grayTemplate)
        
    def match(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        prob, loc, result = super(GrayMatcher, self)._match(img)
        cv2.imshow("graymatch result", result)
        cv2.imshow("graymatch template", self.template)
        return prob, loc
        
        
        
class StartTemplateSearcher():
    INIT_MATCHER_SHAPE = "shape"
    INIT_MATCHER_COLOR = "color"
    
    def __init__(self, template, functionParams):
        '''separate instance of Gray matcher
        because found template will be base for further subprocessing'''
        self.grayMatcher = GrayMatcher(template)
        
        # Additional processors 
        self.matcherInstances = []
        for param in functionParams:
            if param == StartTemplateSearcher.INIT_MATCHER_COLOR:
                self.matcherInstances.append(ColorMatcher(template))
            elif param == StartTemplateSearcher.INIT_MATCHER_SHAPE:
                self.matcherInstances.append(ShapeMatcher(template))
                
    def matchInitTemplate(self, img, verbose):
        
        templateProb, templateLoc = self.grayMatcher.match(img)
        if verbose:
            self.printMatcher(self.grayMatcher, templateProb)
        
        prob = templateProb
        for matcher in self.matcherInstances:
            probTmp, locTmp = matcher.match(img, templateLoc)
            prob *= probTmp
            if verbose:
                self.printMatcher(matcher, probTmp)
        return prob, templateLoc
                
    def printMatcher(self, instance, prob):
        print 'type:\t'+str(type(instance))
        print 'prob:\t'+str(prob)
        print '****************************'
