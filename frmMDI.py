"""
PyRC
An IRC client written in Python and Qt.

PyRC by Michael Allen C. Isaac is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.
http://creativecommons.org/licenses/by-nc-sa/3.0/
"""

from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *

( Ui_frmMDI, QMainWindow ) = uic.loadUiType( 'frmMDI.ui' )

class frmMDI ( QMainWindow ):
    """frmMDI inherits QMainWindow"""

    def __init__ ( self, parent = None ):
        QMainWindow.__init__( self, parent )
        self.ui = Ui_frmMDI()
        self.ui.setupUi( self )
        
        #self.setWindowFlags( Qt.FramelessWindowHint )

    def __del__ ( self ):
        self.ui = None
