# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2015 Soren Bjornstad. All rights reserved.

from PyQt4 import QtGui, QtCore
#from PyQt4.QtGui import QDialog, QInputDialog, QMessageBox, QShortcut, \
#     QKeySequence, QFileDialog
#from PyQt4.QtCore import QObject, QAbstractTableModel, QModelIndex, SIGNAL, SLOT
from ui.forms.busy import Ui_Dialog

import ui.utils
import db.emailing
from db.students import studentsInClass
import db.database as d
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
        self.doClose = False
        self.form.cancelButton.clicked.connect(self.reject)

        self.beginConnect()
        self.thread = WorkerThread()
        self.thread.insertOptions(self.opts, self.cls, self.zid)
        self.thread.finished.connect(self.endOfThread)
        self.thread.emailFailed.connect(self.onError) # error raised, too
        self.thread.serverContacted.connect(self.startProgress)
        self.thread.aboutToEmail.connect(self.updateProgress)
        self.thread.start()

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

    def onError(self, err):
        #print "MOOOOOOOO!"
        raise err
        #ui.utils.errorBox("An error occurred.", "Email error")

    def endOfThread(self):
        #print "EOT function run"
        self.thread.quit()
        #print "thread quitted"
        self.doClose = True
        self.reject()
        #print "reject completed"

    def reject(self):
        if not self.doClose:
            self.thread.exiting = True
            self.form.progressLabel.setText("Canceling...")
        else:
            super(SendingDialog, self).reject()


class WorkerThread(QtCore.QThread):
    serverContacted = QtCore.pyqtSignal(name="serverContacted")
    aboutToEmail = QtCore.pyqtSignal(name="aboutToEmail")
    emailFailed = QtCore.pyqtSignal(Exception, name="emailFailed")

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.SMTPOpen = False
        self.exiting = False
        self.cleanupDone = False

    def __del__(self):
        # I'm not sure we ever actually need a destructor, but since it's
        # working right now, I'm just leaving it in. We can clean it up when
        # I'm not so effing tired of threading problems.
        #print "destructor run"
        if not self.cleanupDone:
            self.tearDown()

    def tearDown(self):
        #print "teardown method run"
        if self.SMTPOpen:
            self.em.closeSMTPConnection()
        d.inter.closeAuxiliaryConnection()
        self.cleanupDone = True
        self.finished.emit()

    def insertOptions(self, opts, cls, zid):
        self.opts = opts
        self.cls = copy.deepcopy(cls)
        self.zid = copy.deepcopy(zid)

    def processEmails(self):
        # take out new database connection to use in this thread; set up emailer
        d.inter.takeOutNewConnection()
        self.em = db.emailing.EmailManager(self.opts, self.cls, self.zid)
        # check if user has canceled and quit if so
        if self.exiting:
            self.tearDown()
            return

        # negotiate a connection with the server
        self.em.openSMTPConnection()
        self.SMTPOpen = True
        if self.exiting:
            self.tearDown()
            return
        self.serverContacted.emit()

        # send email to all students
        studentList = studentsInClass(self.cls)
        numStudents = len(studentList)
        onStudent = 1
        for stu in studentList:
            if self.exiting:
                break
            self.aboutToEmail.emit()
            self.em.sendEmail(stu)
        # done; clean up
        self.tearDown()

    def run(self):
        try:
            self.processEmails()
        except Exception as err:
            #print "error handler caught error"
            # if the destructor is run by another thread, we get an sqlite
            # error, so we need to tear down before we emit the signal
            self.tearDown()
            self.emailFailed.emit(err)
