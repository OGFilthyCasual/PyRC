"""
PyRC
An IRC client written in Python and Qt.

PyRC by Michael Allen C. Isaac is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.
http://creativecommons.org/licenses/by-nc-sa/3.0/
"""

from PyQt4 import uic #QtCore, QtGui
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
    IRCSocket = None
    mdiParent = None
    
    #tell the object listening to onCloseEvent which Channel we are
    onCloseEvent = pyqtSignal( str )
    
    #a word space should be the same size as a printable characterAt
    #in a fixed width font (i hope)
    fontInfo = None
    
    def __init__ ( self, parent = None ):
        QMainWindow.__init__( self, parent )
        self.ui = Ui_frmChannel()
        self.ui.setupUi( self )
        
        f = txtInputFilter( self.ui.txtInput )
        f.registerListener( self )
        
        self.ui.txtInput.installEventFilter( f )
        
        #inserts a table and sets the expectations for column sizes
        self.ui.txtOutput.textCursor().insertHtml('<table width="99%" border="0">')
        
        self.fontInfo = QFontInfo( self.ui.txtOutput.textCursor().charFormat().font() )
        

    
    def __del__ ( self ):
        self.ui = None
        

    #we might get stuffed in an MDI window.
    def setMdiParent( self, obj ):
        self.mdiParent = obj
        self.mdiParent.addSubWindow( self )
        

    def getMdiParent( self ):
        return self.mdiParent
        

    def setIRCSocket( self, socket ):
        self.IRCSocket = socket
        pass

    def sanitizeHtml( self, html ):
        #because we will be using an HTML based display component;
        #it is necessary to replace control characters <> with HTML escape codes.
        
        html = html.replace('<', '&#60;')
        html = html.replace('>', '&#62;')
        
        return html
        
    def ShowMessageAsHTML( self, txt ):
        sb = self.ui.txtOutput.verticalScrollBar()
        
        self.ui.txtOutput.moveCursor(QTextCursor.End)
        self.ui.txtOutput.textCursor().insertHtml( '<br>' + txt )
        
        sb.setValue( sb.maximum() )
        
    
    def ShowMessageAsText( self, txt ):
        sb = self.ui.txtOutput.verticalScrollBar()
        
        self.ui.txtOutput.moveCursor( QTextCursor.End )
        self.ui.txtOutput.textCursor().insertText( '\n' + txt )
        
        sb.setValue( sb.maximum() )
        

    def ShowMessageInTable( self, colOne, colTwo ):
        #I'm sure not this is frowned upon,
        #Once I know a better way I'll update it.
        
        pxSize = self.fontInfo.pixelSize()
        
        t = '''
            <tr>
                <td align="right" style="background-color:#EEEEEE;width:150px;float:left;">
                    $colOne
                </td>
                <td align="left" style="background-color:#FFFFFF;width:0px;float:left;">
                    $colTwo
                </td>
            </tr>
            ''' #% str(pxSize * 18)
        
        #print(x)
        
        sb = self.ui.txtOutput.verticalScrollBar()
        
        self.ui.txtOutput.moveCursor(QTextCursor.End)
        self.ui.txtOutput.textCursor().insertHtml( t.replace('$colOne', colOne).replace('$colTwo', colTwo))
        
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
        #this is the prefixed name of the user.
        if (name in list(self.names)):
            nick = self.names[name] + name
            
            #this is a very dirty line, but it works.
            try:
                self.ui.listNames.takeItem( self.ui.listNames.row( self.ui.listNames.findItems(nick, Qt.MatchExactly)[0] ) )
            finally:
                pass
            
            del self.names[name]
            
        return

    #add names to the channel
    def addNames( self, nnames = {} ):
        
        #self.names = (self.names + nlist)
        
        #merge names with the existing
        self.names.update( nnames )
        
        for n in list(nnames.keys()):
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
        

    def processInput( self, caller, txt ):
        #this function is required by the txtInputFilter class so that
        #this object will recieve input from the event filter.

        txt = self.sanitizeHtml( txt )

        if (self.IRCSocket):
            if(txt[0] == '/'):
                self.IRCSocket.send( txt[1:] + '\r\n' )
                self.ShowMessageInTable( '<b>&#60;&#60;&#60; sent &#62; ', txt[1:] )
            else:
                self.IRCSocket.send('PRIVMSG %s :%s\r\n' % (self.channel, txt))
                self.ShowMessageInTable(('&#60;<font color=blue>%s</font>&#62;' % self.IRCSocket.getNick()), txt)
            
        return
        