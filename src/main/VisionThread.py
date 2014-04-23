'''
Created on Dec 1, 2012

@author: karsten
'''
import threading
from vision import HandCommands

class VisionThread(threading.Thread):

    def __init__(self, trajectoryQueue):
        self.hand = HandCommands.Handcommands(trajectoryQueue)
        threading.Thread.__init__(self)
        
    def run(self):
        self.hand.startMainLoop()
        print 'vision ended thread'
