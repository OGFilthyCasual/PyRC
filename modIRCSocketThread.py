"""
PyRC
An IRC client written in Python and Qt.

PyRC by Michael Allen C. Isaac is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.
http://creativecommons.org/licenses/by-nc-sa/3.0/
"""

#A threaded socket which parses IRC messages in to managable
#dictionary packets for consumption

import asyncore, socket

from PyQt4.QtCore import QThread, QObject, pyqtSignal

class IRCSocketThread(asyncore.dispatcher, QThread):
    nick = None
    user = None
    passwd = 'none'
    buffer = ''
    
    #connect a function to this signal that you wish to recive lines from the IRC server
    PacketEmitter = pyqtSignal( dict )
    
    def __init__( self, parent=None ):
        self.nick = ('pythonTestClient')
        self.user = 'IRCSocketThread@Python'
        self.passwd = ''

        QThread.__init__( self, parent )
        asyncore.dispatcher.__init__( self, parent )
        
        self.create_socket( socket.AF_INET, socket.SOCK_STREAM )
        self.setblocking(1)

    def __del__( self ):
        self = None
        

    def getNick( self ):
        return self.nick 
        

    def setNick( self, data, sendCommand = False ):
        self.nick = data
        
        if( sendCommand == True ):
            self.send('NICK %s\r\n' % data )
        

    def setUser( self, data, sendCommand = False ):
        self.user = data
        
        if( sendCommand == True ):
            self.send('USER %s - - %s\n' % (data, ':Python-2.7.3'))
            self.send('USERHOST %s\n' % data)
            

    def setPass( self, data, sendCommand = False ):
        self.passwd = data
        
        if( sendCommand == True ):
            self.send('PASS %s\r\n' % data )
            

    def extractNick( self, prefix ):
        if ('!' in prefix):
            return prefix.split('!')[0]
        else:
            return prefix

    def extractUser( self, prefix ):
        if (('!' in prefix) and ('@' in prefix)):
            return prefix.split('@')[0].split('!')[1] #ahahah
        else:
            return prefix

    def extractHost( self, prefix ):
        if ('@' in prefix):
            return prefix.split('@')[1]
        else:
            return prefix


    def parseMessage(self, msg):

        #PREFIX (optional)     COMMAND      ARGS          MESSAGE
        #:[server | hostmask]  [str | int]  {[str] ... }  :[str]

        p = ''
        c = ''
        a = []
        m = ''

        #our return value
        packet = { }
        
        msg = msg.strip('\r')
        
        #explode the entire line at spaces
        parts = msg.split(' ')
        
        if(parts[0][0] == ':'):
            #if the line being with a colon are messages from the either
            #server (notices, etc) or another users hostname (privmsg, etc).
            #This is known as the prefix which is followed by a command.
            
            p = parts[0]
            c = parts[1]
        else:
            #if there is no colon, we're reciving a command (pong, etc)
            #from the server
            p = ''
            c = parts[0]
            
        
        #cut the message line down to the remainder after the command
        msg = msg[((len(p)+ len(c))+2):]
        
        #explode the remainder
        parts = msg.split(' ')
        
        #step throuh each part
        x = 0
        while (x < len(parts)):
            
            if(parts[x][0] == ':'):
                #the argument that begins with a colon starts the trailing message
                #we also drop the leading colon
                m = str.join(' ', parts[x:])[1:]
                
                break
            else:
                #all other arguments are just that; arguments
                a.append( parts[x] )

            x = x + 1
        
        #assemble the packet and return it, it will then be emitted
        #the next component of the client
        
        #drop the leading colon from the prefix
        
        packet['p'] = p[1:]
        packet['c'] = c
        packet['a'] = a
        packet['m'] = m
        
        return packet
        


    def handle_connect( self ):
        print 'Connected.'
        
        self.send( 'PASS none\n' )
        self.send( 'NICK %s\n' % self.nick )
        self.send( 'USER %s - - %s\n' % (self.user, ':Python-2.7.3') )
        self.send( 'USERHOST %s\n' % self.user )

    def handle_close( self ):
        self.close()
        

    def handle_read( self ):

        rbuffer = ''

        while (1):
            c = self.recv(1)
            if (c == '\n'):
                self.PacketEmitter.emit( self.parseMessage( rbuffer ) )
                rbuffer = ''
            else:
                rbuffer = rbuffer + c
            

    def writable( self ):
        return (len(self.buffer) > 0)
        

    def handle_write( self ):
        sent = self.send( self.buffer )
        self.buffer = self.buffer[sent:]
        

    def run( self ):
        asyncore.loop()
        