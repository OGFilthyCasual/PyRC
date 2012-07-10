from PyQt4 import uic

( Ui_frmMDI, QMainWindow ) = uic.loadUiType( 'frmMDI.ui' )

class frmMDI ( QMainWindow ):
    """frmMDI inherits QMainWindow"""

    def __init__ ( self, parent = None ):
        QMainWindow.__init__( self, parent )
        self.ui = Ui_frmMDI()
        self.ui.setupUi( self )

    def __del__ ( self ):
        self.ui = None
