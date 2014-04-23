'''
Created on Dec 1, 2012

@author: karsten
'''
import telnetlib

class TelnetVLC(object):
    def __init__(self, hostserver='127.0.01', hostport='4212', password='admin'):
        # telnet connection
        self.newline = "\n"
        self.telnet = telnetlib.Telnet(hostserver,hostport)
        self.telnet.read_until("Password: ")
        self.telnet.write(password +  self.newline)
        
    def executeCommand(self, command):
        # send comments after receiving "> "
        self.telnet.read_until("> ")
        self.telnet.write(command+self.newline)
        
    def closeConnection(self):
        self.telnet.close()
        
        
if __name__ == '__main__':
    vlc = TelnetVLC()
    vlc.executeCommand('pause')
    vlc.closeConnection()