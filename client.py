# -*- coding: utf-8 -*-

# Copyright (c) 2011 Filippenok Dmitriy <fil@fillis.nsk.ru>
#
from PyQt4.QtCore import *
from PyQt4.QtNetwork import *
from PyQt4.QtGui import *
import sys

__author__ = 'Filin'


from PyQt4 import QtCore, QtGui, QtNetwork


class DialogClient(QtGui.QDialog):
    TotalBytes = 50 * 1024 * 1024
    PayloadSize = 65536

    def __init__(self, parent=None):
        super(DialogClient, self).__init__(parent)

        self.tcpClient = QtNetwork.QTcpSocket()
        self.bytesToWrite = 0
        self.bytesWritten = 0
        self.bytesReceived = 0

        self.clientProgressBar = QtGui.QProgressBar()
        self.clientStatusLabel = QtGui.QLabel("Client ready")

        self.startButton = QtGui.QPushButton("&Start")
        self.quitButton = QtGui.QPushButton("&Quit")

        buttonBox = QtGui.QDialogButtonBox()
        buttonBox.addButton(self.startButton, QtGui.QDialogButtonBox.ActionRole)
        buttonBox.addButton(self.quitButton, QtGui.QDialogButtonBox.RejectRole)

        self.startButton.clicked.connect(self.start)
        self.quitButton.clicked.connect(self.close)
        self.tcpClient.connected.connect(self.startTransfer)
        self.tcpClient.bytesWritten.connect(self.updateClientProgress)
        self.tcpClient.error.connect(self.displayError)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.clientProgressBar)
        mainLayout.addWidget(self.clientStatusLabel)
        mainLayout.addStretch(1)
        mainLayout.addSpacing(10)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("Loopback")

    def start(self):
        self.startButton.setEnabled(False)

        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        self.bytesWritten = 0
        self.bytesReceived = 0

        self.clientStatusLabel.setText("Connecting")

        self.tcpClient.connectToHost(QtNetwork.QHostAddress(QtNetwork.QHostAddress.LocalHost), 9112)


    def startTransfer(self):
        self.bytesToWrite = DialogClient.TotalBytes - self.tcpClient.write(QtCore.QByteArray('String\n'))
        self.clientStatusLabel.setText("Connected")

    def updateClientProgress(self, numBytes):
        self.bytesWritten += numBytes
        if self.bytesToWrite > 0:
            self.bytesToWrite -= self.tcpClient.write(QtCore.QByteArray('String\n'))

        self.clientProgressBar.setMaximum(DialogClient.TotalBytes)
        self.clientProgressBar.setValue(self.bytesWritten)
        self.clientStatusLabel.setText("Sent %dMB" % (self.bytesWritten / (1024 * 1024)))

    def displayError(self, socketError):
        if socketError == QtNetwork.QTcpSocket.RemoteHostClosedError:
            return

        QtGui.QMessageBox.information(self, "Network error",
                "The following error occured: %s." % self.tcpClient.errorString())

        self.tcpClient.close()
        self.clientProgressBar.reset()
        self.clientStatusLabel.setText("Client ready")
        self.startButton.setEnabled(True)
        QtGui.QApplication.restoreOverrideCursor()


if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    dialog = DialogClient()
    dialog.show()
    sys.exit(dialog.exec_())
