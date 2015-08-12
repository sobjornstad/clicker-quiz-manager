# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2015 Soren Bjornstad. All rights reserved.

from PyQt4 import QtGui, QtCore
#from PyQt4.QtGui import QDialog, QInputDialog, QMessageBox, QShortcut, \
#     QKeySequence, QFileDialog
#from PyQt4.QtCore import QObject, QAbstractTableModel, QModelIndex, SIGNAL, SLOT
from ui.forms.busy import Ui_Dialog

import db.emailing
from db.students import studentsInClass
from time import sleep
import copy

class SendingDialog(QtGui.QDialog):
    def __init__(self, parent, optsDict, cls, zid):
        QtGui.QDialog.__init__(self)
        self.form = Ui_Dialog()
        self.form.setupUi(self)
        self.parent = parent
        self.opts = optsDict
        self.cls = cls
        self.zid = zid

        self.beginConnect()
        self.thread = WorkerThread()
        self.thread.insertOptions(self.opts, self.cls, self.zid)
        self.thread.finished.connect(self.endOfThread)
        self.thread.serverContacted.connect(self.startProgress)
        self.thread.aboutToEmail.connect(self.updateProgress)
        self.thread.start()

        #self.form.cancelButton.clicked.connect(self.reject)
        #self.beginSend()

    def beginConnect(self):
        self.form.progressBar.setMinimum(0)
        self.form.progressBar.setMaximum(0)
        self.form.progressBar.setValue(-1)
        self.form.progressLabel.setText("Connecting to server...")

    def startProgress(self):
        self.totalStudents = len(studentsInClass(self.cls))
        self.form.progressBar.setMinimum(0)
        self.form.progressBar.setMaximum(self.totalStudents)
        self.form.progressBar.setValue(0)

    def updateProgress(self):
        newVal = self.form.progressBar.value() + 1
        self.form.progressBar.setValue(newVal)
        self.form.progressLabel.setText("Sending mail (%i/%i)..." % (
                newVal, self.totalStudents))

    def endOfThread(self):
        print "reached endOfThread"
        self.thread.quit()
        self.reject()


        #self.thread = QtCore.QThread()
        #obj = Worker()
        #obj.moveToThread(self.thread)
        #obj.finished.connect(self.thread.quit)
        ###self.thread.started.connect(obj.myMethod)
        ###self.thread.finished.connect(self.endOfThread)
        ###self.thread.start()
        ###self.thread.started.emit()
        ###print "thread started"


        #self.thread.finished.connect(self.finishSend)
        #self.thread.terminated.connect(self.finishSend)
        #self.thread.connectedToServer.connect(self.startProgress)
        #self.connect(self.thread, SIGNAL("connectFinished__()"),
        #        self.startProgress)
        #self.connect(self.thread, SIGNAL("studentDone()"),
                #self.updateProgress)
        #print "reached end of connections"
        #QtGui.QApplication.processEvents()

    def moo(self):
        print "moooooo"

    #def finishSend(self):
    #    self.reject()


    def reject(self):
        # take care of canceling the mail
        super(SendingDialog, self).reject()

class WorkerThread(QtCore.QThread):
    serverContacted = QtCore.pyqtSignal(name="serverContacted")
    aboutToEmail = QtCore.pyqtSignal(name="aboutToEmail")

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)

    def insertOptions(self, opts, cls, zid):
        self.opts = copy.deepcopy(opts)
        self.cls = copy.deepcopy(cls)
        self.zid = copy.deepcopy(zid)

    def run(self):
        print "started connection attempt"
        sleep(1)
        #TODO: somehow we need to get this using a new connection from database.takeOutNewConnection()
        #self.em = db.emailing.EmailManager(self.opts, self.cls, self.zid)
        print "email manager setup"
        #em.openSMTPConnection()
        print "smtp connection opened"
        #self.serverContacted.emit()
        #em.closeSMTPConnection() # remove shortly
        print "smtp connection closed"
        print "SMTP open"

        #self.aboutToEmail.emit()
        #sleep(1)
        #self.aboutToEmail.emit()
        #sleep(1)
        print "now terminating." # implied self.finished.emit()

# class Worker(QtCore.QObject):
#     #connectedToServer = QtCore.pyqtSignal(int, name="connectedToServer")
#     finished = QtCore.pyqtSignal()
# 
#     #def __init__(self):#, opts, cls, zid):
#     #    QtCore.QObject.__init__(self)
#         #self.opts = opts
#         #self.cls = cls
#         #self.zid = zid
#         #self.opts = copy.deepcopy(opts)
#         #self.cls = copy.deepcopy(cls)
#         #self.zid = copy.deepcopy(zid)
#         #self.exiting = False
# 
#     #def __del__(self):
#     #    "Notify self that it should terminate and wait for it to do so."
#     #    self.exiting = True
#     #    self.wait()
#     #    QtCore.QThread.__del__(self)
# 
#     @QtCore.pyqtSlot()
#     def myMethod(self):
#         self.finished.emit()
#         #print "running myMethod"
#         #print "emitted"
#         #self.connectedToServer.emit(5)
# 
#         #studentList = studentsInClass(self.cls)
#         #numStudents = len(studentList)
#         #onStudent = 1
#         #for stu in studentList:
#         #    print "sending new student"
#         #    if self.exiting:
#         #        break
#         #    em.sendEmail(stu)
#         #print "send done"
#         #em.closeSMTPConnection()
#         #print "conn closed"
# 
# 
