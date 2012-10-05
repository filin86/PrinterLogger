# -*- coding: utf-8 -*-

# Copyright (c) 2011 Filippenok Dmitriy <fil@fillis.nsk.ru>
#
from PyQt4.QtGui import *
from PyQt4.QtCore import Qt, QTextStream, QThread, pyqtSignal, QDataStream
from PyQt4.QtNetwork import QTcpServer, QTcpSocket

__author__ = 'Filin'


class MainWindow(QMainWindow):

    port = 9112

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        widget = QWidget()
        self.layout = QVBoxLayout()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

        self.status = self.statusBar()

        self.server = PrinterLoggerServer()

        if not self.server.listen(port=self.port):
            QMessageBox.critical(self, 'Printer Logger', 'Unable to start server: {}'.format(self.tcpServer.errorString()))
            self.close()
            return

        self.status.showMessage('The Printer Logger is running on port: {}'.format(self.server.serverPort()))

        quitButton = QPushButton('Exit')
        quitButton.clicked.connect(self.close)
        self.layout.addWidget(quitButton)

        self.setWindowTitle('Printer Logger 0.1')

    def newConnect(self):
        self.connection = self.tcpServer.nextPendingConnection()
        self.connection.disconnected.connect(self.connection.deleteLater)

        self.text = QTextStream(self.connection)


class PrinterLoggerServer(QTcpServer):
    def __init__(self, parent=None):
        super(PrinterLoggerServer, self).__init__(parent)

    def incomingConnection(self, socketDescriptor):
        thread = PrinterLoggerThread(socketDescriptor, self)
        thread.finished.connect(thread.deleteLater)
        thread.start()

class PrinterLoggerThread(QThread):

    error = pyqtSignal(QTcpSocket.SocketError)

    def __init__(self, sockDescriptor, parent):
        super(PrinterLoggerThread, self).__init__(parent)

        self.socketDescriptor = sockDescriptor

        self.shoudDisconnect = False

    def run(self):
        tcpSocket = QTcpSocket()
        if not tcpSocket.setSocketDescriptor(self.socketDescriptor):
            self.error.emit(tcpSocket.error())
            return

        self._stream = QDataStream(tcpSocket)

        print('text stream created')
        while not self.shoudDisconnect:
            print(tcpSocket.bytesAvailable())
            while tcpSocket.bytesAvailable():
                pass
