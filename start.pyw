# -*- coding: utf-8 -*-

# Copyright (c) 2011 Filippenok Dmitriy <fil@fillis.nsk.ru>
#
import sys
from PyQt4.QtGui import QApplication
from server import Dialog

__author__ = 'Filin'

if __name__ == '__main__':

    app = QApplication(sys.argv)
    dialog = Dialog()
    dialog.show()
    sys.exit(dialog.exec_())
