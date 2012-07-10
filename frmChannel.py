from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from modInputFilter import txtInputFilter

( Ui_frmChannel, QMainWindow ) = uic.loadUiType( 'frmChannel.ui' )

#i need a way to tell the main window when a channel closes.
#probably need a to setup a signal for it.

class frmChannel ( QMainWindow ):
    """frmChannel inherits QMainWindow"""

    ui = None
    
    #string containing the name of the IRC Channel
    channel = None
    
    #topic of the channel
    topic = ''
    
    #names on the channel, we use a dict for name/mode data,
    #where the nicknames are keys, and the data is user modes (@+)
    names = {}
    
    #mmhmmmm.
    frmMain = None
    
    #tell the object listening to onCloseEmitter which Channel we are
    onCloseEvent = pyqtSignal( str )
    
    def __init__ ( self, parent = None ):
        QMainWindow.__init__( self, parent )
        self.ui = Ui_frmChannel()
        self.ui.setupUi( self )
        
        f = txtInputFilter( self.ui.txtInput )
        f.registerListener( self )
        
        self.ui.txtInput.installEventFilter( f )
        

    def __del__ ( self ):
        self.ui = None
        

    def ShowMessageAsHTML( self, txt ):
        sb = self.ui.txtOutput.verticalScrollBar()
        
        self.ui.txtOutput.moveCursor(QTextCursor.End)
        self.ui.txtOutput.textCursor().insertHtml( txt + '<br>')
        
        sb.setValue( sb.maximum() )
        
    
    def ShowMessageAsText( self, txt ):
        sb = self.ui.txtOutput.verticalScrollBar()

        self.ui.txtOutput.moveCursor( QTextCursor.End )
        self.ui.txtOutput.textCursor().insertText( txt + '\n' )
        
        sb.setValue( sb.maximum() )
        
    def closeEvent(self, event):
        #when we close, notify other objects (probably frmMain)
        #when this signal is emitted, its converted from string to QString on
        #the other side.
        if (self.channel):
            self.onCloseEvent.emit( self.channel )
        

    def addName( self, name ):
        
        self.names[name] = ''
        self.ui.listNames.addItem( name )
        
        pass
        

    def removeName( self, name ):
        pass
        

    #add names to the channel
    def addNames( self, nnames = {} ):
        
        #self.names = (self.names + nlist)
        
        #merge names with the existing
        self.names.update( nnames )
        
        for n in nnames.keys():
            #add the data first because it will contain a mode character if any
            self.ui.listNames.addItem( self.names[n] + n )
            
        return
        

    #return the dict of names
    def getNames( self ):
        return self.names
        

    #string
    def getChannel( self ):
        return self.channel
        
    
    #string
    def setChannel( self, chn ):
        self.channel = chn
        

    def setFormMain( self, frm ):
        self.frmMain = frm
        pass 

    def processInput( self, caller, txt ):
        #this function is required by tge txtInputFilter class so that
        #this object will recieve input from the event filter.
        
        if(self.frmMain):
            self.frmMain.send('PRIVMSG %s :%s' % (self.channel, txt))
            self.ShowMessageAsHTML('&#60;<b><font color=blue>%s</font></b>&#62; %s' % (self.frmMain.ircsocket.getNick(), txt))
            
        return
        