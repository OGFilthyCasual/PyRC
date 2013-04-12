"""
PyRC
An IRC client written in Python and Qt.

PyRC by Michael Allen C. Isaac is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.
http://creativecommons.org/licenses/by-nc-sa/3.0/
"""

from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *

( Ui_frmConnect, QMainWindow ) = uic.loadUiType( 'frmConnect.ui' )

class frmConnect ( QMainWindow ):

    def __init__ ( self, parent = None ):
        QMainWindow.__init__( self, parent )

        self.ui = Ui_frmConnect()
        self.ui.setupUi( self )

        pass
