"""
PyRC
An IRC client written in Python and Qt.

PyRC by Michael Allen C. Isaac is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.
http://creativecommons.org/licenses/by-nc-sa/3.0/
"""

import sys

# import PyQt4 QtCore and QtGui modules
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from frmMDI import frmMDI
from frmMain import frmMain

def Main():
    if __name__ == '__main__':

        # create application
        app = QApplication( sys.argv )
        app.setApplicationName( 'PyRC' )

        #app.setStyle( QStyleFactory.create('plastique') )
        
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
