'''
Created on Dec 8, 2012

@author: karsten
'''
import Xlib.X as X
import Xlib.display as display
import Xlib.ext.xtest as xtest
import time

class InputSimulator(object):
    def __init__(self):
        self.disp = display.Display()
        self.root = self.disp.screen().root
    
class KeystrokeSimulator(InputSimulator):

    def __init__(self):
        InputSimulator.__init__(self)
        self.key = self.disp.keysym_to_keycode(ord(' '))
        
    def sendKey(self):
        xtest.fake_input(self.root, X.KeyPress, self.key)
        xtest.fake_input(self.root, X.KeyRelease, self.key)
        self.disp.flush()
        
class MousepointerSimulator(InputSimulator):

    def __init__(self, currentLoc):
        InputSimulator.__init__(self)
        self.currentLoc = currentLoc
        
    def setStartPosition(self, loc):
        self.currentLoc = loc
        
    def moveToPoint(self, loc, sleepTime = 0.01):
        self.root.warp_pointer(loc[0], loc[1])
        self.disp.sync()
        time.sleep(sleepTime)
        
    def movePoints(self, locArray):
        for loc in locArray:
            self.moveToPoint(loc, 0.1/len(locArray))

        