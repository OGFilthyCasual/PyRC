import sys

# import PyQt4 QtCore and QtGui modules
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from frmMDI import frmMDI
from frmChannel import frmChannel
from frmMain import frmMain

def Main():
    if __name__ == '__main__':

        # create application
        app = QApplication( sys.argv )
        app.setApplicationName( 'Sortes' )

        # create widget
        #w = frmMain()
        #w = frmChannel()
        
        m = frmMDI()
        w = frmMain()
        
        w.setMdiParent( m.ui.mdiArea )
        w.showMaximized()
        
        m.show()
        
        # connection
        QObject.connect( app, SIGNAL( 'lastWindowClosed()' ), app, SLOT( 'quit()' ) )

        # execute application
        sys.exit( app.exec_() )


Main()
