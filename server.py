# -*- coding: utf-8 -*-

# Copyright (c) 2011 Filippenok Dmitriy <fil@fillis.nsk.ru>
#
from PyQt4.QtCore import QDir, QFile, QSettings, QFileInfo, QTextStream
from PyQt4.QtGui import *
from PyQt4.QtNetwork import QTcpServer, QTcpSocket

__author__ = 'Filin'


class Dialog(QDialog):
    TotalBytes = 50 * 1024 * 1024
    PayloadSize = 65536

    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent)

        self.settings = QSettings('settings.ini', QSettings.IniFormat)
        self.tcpServer = QTcpServer()

        self.chBox = QCheckBox("Print log to window")
        self.text = QPlainTextEdit()
        self.serverStatusLabel = QLabel("Server ready")

        self.lblFileName = QLabel("Choose file before start!")
        self.saveButton = QPushButton("&Choose file...")
        self.startButton = QPushButton("&Start")
        self.stopButton = QPushButton("S&top")
        self.quitButton = QPushButton("&Quit")
        
        self.file = None
        self.tcpServerConnection = None

        self._lineCounter = 0
        self._lineBuf = ''

        buttonBox = QDialogButtonBox()
        buttonBox.addButton(self.startButton, QDialogButtonBox.ActionRole)
        buttonBox.addButton(self.stopButton, QDialogButtonBox.RejectRole)
        buttonBox.addButton(self.quitButton, QDialogButtonBox.RejectRole)

        clearButon = QPushButton('&Clear')

        self.saveButton.clicked.connect(self.savedlg)
        self.startButton.clicked.connect(self.start)
        self.stopButton.clicked.connect(self.stopClicked)
        self.quitButton.clicked.connect(self.close)
        clearButon.clicked.connect(self.text.clear)
        self.tcpServer.newConnection.connect(self.acceptConnection)

        saveLayout = QHBoxLayout()
        saveLayout.addWidget(self.lblFileName)
        saveLayout.addStretch(1)
        saveLayout.addWidget(self.saveButton)

        topTextLayout = QHBoxLayout()
        topTextLayout.addWidget(self.chBox)
        topTextLayout.addStretch(1)
        topTextLayout.addWidget(clearButon)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(saveLayout)
        mainLayout.addLayout(topTextLayout)
        mainLayout.addWidget(self.text)
        mainLayout.addWidget(self.serverStatusLabel)
#        mainLayout.addStretch(1)
        mainLayout.addSpacing(10)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

        self.title = "Simple Logger"
        self.ver = '1.0'

        self.setWindowIcon(QIcon('./icon.png'))
        self.setWindowTitle("{} {}".format(self.title, self.ver))

    def start(self):
        if self.file is None:
            QMessageBox.critical(self, self.title, "Unable open log file.\nPlease, select another file.")
            return
        self.startButton.setEnabled(False)

        while not self.tcpServer.isListening() and not self.tcpServer.listen(port=9112):
            ret = QMessageBox.critical(self, self.title,
                    "Unable to start the test: %s." % self.tcpServer.errorString(),
                    QMessageBox.Retry | QMessageBox.Cancel)
            if ret == QMessageBox.Cancel:
                return

        self.serverStatusLabel.setText("Waiting connection ...")

    def acceptConnection(self):
        self.tcpServerConnection = self.tcpServer.nextPendingConnection()
        self.tcpServerConnection.readyRead.connect(self.updateLog)
        self.tcpServerConnection.error.connect(self.displayError)

        self.file = QFile(self.filename)
        if not self.file.open(QFile.Append):
            QMessageBox.warning(self, self.title, "Unable to write file {}:\n{}.".format(self.filename, self.file.errorString()))
            self.file = None
            return
        self.textStream = QTextStream(self.file)
        self.textStream.setCodec('UTF-8')

        self.serverStatusLabel.setText("Logging ...")
        self.tcpServer.close()

    def savedlg(self):
        self.filename = QFileDialog.getSaveFileName(self, "Log Filename", self.settings.value('directories/dir_save', QDir.currentPath()), "Text (*.log *.txt);;All (*)")
        if not self.filename:
            return

        self.file = QFile(self.filename)
        self.lblFileName.setText(self.filename)
        if not self.file.open(QFile.WriteOnly):
            QMessageBox.warning(self, self.title, "Unable to write file {}:\n{}.".format(self.filename, self.file.errorString()))
            self.file = None
            return
        self.textStream = QTextStream(self.file)
        self.textStream.setCodec('UTF-8')

        self.settings.setValue('directories/dir_save', QFileInfo(self.file).path())
        self.file.close()

    def updateLog(self):
        if self.tcpServerConnection.bytesAvailable():
            data = self.tcpServerConnection.readAll()
            line = "{}".format(str(data.data().decode()))
            if self.chBox.isChecked():
                self._lineCounter += 1
                self._lineBuf += line
                if self._lineCounter > 10:
                    self.text.appendPlainText(self._lineBuf)
                    self._lineCounter = 0
                    self._lineBuf = ''
            self.textStream << line
            self.file.flush()
#            self.serverStatusLabel.setText(line)

    def closeEvent(self, event):
        if self.file is not None:
            self.file.flush()
            self.file.close()

    def stopClicked(self):
        if self.tcpServerConnection is not None:
            self.tcpServerConnection.close()
        self.file.close()
        self.startButton.setEnabled(True)
        self.serverStatusLabel.setText("Logger ready")


    def displayError(self, socketError):
        if socketError == QTcpSocket.RemoteHostClosedError:
            return

        QMessageBox.information(self, "Network error",
                "The following error occured: %s." % self.tcpServer.errorString())

        self.tcpServer.close()
        self.file.close()
        self.serverStatusLabel.setText("Logger ready")
        self.startButton.setEnabled(True)


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    dialog = Dialog()
    dialog.show()
    sys.exit(dialog.exec_())
