"""
PyRC
An IRC client written in Python and Qt.

PyRC by Michael Allen C. Isaac is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.
http://creativecommons.org/licenses/by-nc-sa/3.0/
"""

from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from modInputFilter import txtInputFilter

( Ui_frmPrivate, QMainWindow ) = uic.loadUiType( 'frmPrivate.ui' )

class frmPrivate ( QMainWindow ):
    """frmPrivate inherits QMainWindow"""

    #dict of names, which contain a QTextDocument() for each person
    nnames = {}
    
    IRCSocket = None
    mdiParent = None

    #a word space should be the same size as a printable characterAt
    #in a fixed width font (i hope)
    fontInfo = None
    
    def __init__ ( self, parent = None ):
        QMainWindow.__init__( self, parent )
        self.ui = Ui_frmPrivate()
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
        
    
    def addName( self, nname ):
        self.names[nname] = QtGui.QTextDocument()
        self.ui.listNames.addItem( nname )
        return
        

    def removeName( self, nname ):
        #this is a very dirty line, but it works.
        self.ui.listNames.takeItem( self.ui.listNames.row( self.ui.listNames.findItems(nname, Qt.MatchExactly)[0] ) )
    
        del self.names[nname]
            
        return
        
    
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
        
    
    def processInput( self, caller, txt ):
        #this function is required by the txtInputFilter class so that
        #this object will recieve input from the event filter.

        txt = self.sanitizeHtml( txt )

        if (self.IRCSocket):
            if(txt[0] == '/'):
                self.IRCSocket.send( txt[1:] + '\r\n' )
                self.ShowMessageInTable( '<b>&#60;&#60;&#60; sent &#62; ', txt[1:] )
            else:
                #self.IRCSocket.send('PRIVMSG %s :%s\r\n' % (self.channel, txt))
                self.ShowMessageInTable(('&#60;<font color=blue>%s</font>&#62;' % self.IRCSocket.getNick()), txt)
            
        
        return
        
    