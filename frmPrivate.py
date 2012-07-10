from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *


( Ui_frmPrivate, QMainWindow ) = uic.loadUiType( 'frmPrivate.ui' )

class frmPrivate ( QMainWindow ):
    """frmPrivate inherits QMainWindow"""

    def __init__ ( self, parent = None ):
        QMainWindow.__init__( self, parent )
        self.ui = Ui_frmPrivate()
        self.ui.setupUi( self )

    def __del__ ( self ):
        self.ui = None

