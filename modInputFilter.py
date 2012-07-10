"""
PyRC
An IRC client written in Python and Qt.

PyRC by Michael Allen C. Isaac is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.
http://creativecommons.org/licenses/by-nc-sa/3.0/
"""

from PyQt4.QtCore import *

class txtInputFilter( QObject ):

    """
        example code taken from http://stackoverflow.com/questions/2276810/pyqt-typeerror
        
        This class is meant to be used exclusivly with QPlainTextEdit
        
        def registerListener(self, obj) -- 
        this method will specify an object to recive text via processInput()
        
        def processInput( self, caller, txt ) --
        API:  define this method inside of the object that will recieve text from this txtInputFilter
        
        example:
            #self.ui.txtInput is a QtGui.QPlainTextEdit
            f = txtInputFilter( self.ui.txtInput )
        
            #self is a QtGui.QMainWindow, and contains the API method: def processInput( self, caller, txt )
            f.registerListener( self )  
        
            #install the event filter
            self.ui.txtInput.installEventFilter( f )
        
    """

    objListener = None
    listHistory = [ ]
    listHistoryPos = None

    def __init__(self, parent = None):
        super(txtInputFilter, self).__init__( parent )
        

    def __del__ ( self ):
        self.ui = None
        

    def eventFilter(self, obj, event):
        if (event.type() == QEvent.KeyPress):
            
            #here we can intercept a given key
            if ((event.key() == Qt.Key_Return) or (event.key() == Qt.Key_Enter)):
                
                if((self.objListener) and (hasattr( self.objListener, 'processInput' ))):
                    
                    #add our input to the list
                    self.listHistory.append( obj.toPlainText() )
                    
                    #mark the highest bound element
                    self.listHistoryPos = len(self.listHistory)
                    
                    #call the listener
                    self.objListener.processInput( obj, obj.toPlainText() )
                    
                    #clear the plain edit box
                    obj.setPlainText('')
                    
                    print self.listHistoryPos
                    
                else:
                    print 'txtInputFilter::objListener is undefined or does not support processInput()'
                
                return True
                
            elif (event.key() == Qt.Key_Up):
                if((self.listHistoryPos == None) or ((self.listHistoryPos - 1) < 0)):
                    return True
                else:
                    self.listHistoryPos = self.listHistoryPos - 1
                    obj.setPlainText( self.listHistory[ (self.listHistoryPos) ] )
                    
                
                return True
                
            elif (event.key() == Qt.Key_Down):
                if(self.listHistoryPos == None):
                    return True
                
                if ((self.listHistoryPos + 1) < len(self.listHistory)):
                    self.listHistoryPos = self.listHistoryPos + 1
                    obj.setPlainText( self.listHistory[ (self.listHistoryPos) ] )
                    
                
                return True
                
            else:
                return QObject.eventFilter(self, obj, event)
            
        else:
            #all other events are passed through
            return QObject.eventFilter(self, obj, event)
            

    def registerListener(self, obj):
        if(hasattr( obj, 'processInput' )):
            #we should only set objListener if it contains the processInput function
            self.objListener = obj
        else:
            print 'txtInputFilter::registerListener object does not support processInput()'
        
        return
        