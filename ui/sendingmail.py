# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2015 Soren Bjornstad. All rights reserved.

from PyQt4 import QtGui, QtCore
#from PyQt4.QtGui import QDialog, QInputDialog, QMessageBox, QShortcut, \
#     QKeySequence, QFileDialog
#from PyQt4.QtCore import QObject, QAbstractTableModel, QModelIndex, SIGNAL, SLOT
from ui.forms.busy import Ui_Dialog

import socket
import smtplib
import sys, traceback # debug

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
        self.hadError = False
        self.recipientErrors = []
        self.form.cancelButton.clicked.connect(self.reject)

        # Make absolutely sure db is synced up before opening a concurrent
        # connection in the worker thread (we shouldn't need to have committed,
        # but just in case).
        d.inter.forceSave()
        self.beginConnect()
        self.thread = WorkerThread()
        self.thread.insertOptions(self.opts, self.cls, self.zid)
        self.thread.finished.connect(self.endOfThread)
        self.thread.emailFailed.connect(self.onError)
        self.thread.recipientRefused.connect(self.onRecipientRefused)
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

    def onRecipientRefused(self, err):
        self.recipientErrors.append(err.recipients.values()[0])
        self.hadError = True

    def onError(self, err, tbList):
        self.hadError = True
        eb = ui.utils.errorBox
        try:
            ui.utils.tracebackBox("%r\n%s" % (err, str(tbList)))
        except socket.gaierror as e:
            if 'Name or service not known' in e:
                eb("Could not connect to the SMTP server specified. Please "
                   "check the hostname for accuracy; if problems continue, "
                   "you may have a firewall or internet connection problem.",
                   "Could not resolve SMTP hostname")
        except smtplib.SMTPServerDisconnected as e:
            eb("The server disconnected unexpectedly. Maybe you have the "
               "SSL or port options wrong?",
               "Server disconnected")
        except smtplib.SMTPSenderRefused as e:
            eb("The server does not allow you to send email from the email "
               "address you specified (%s). The full error is as "
               "follows:\n\n%s" % (e.sender, e.smtp_error),
               "Permission denied")
        except smtplib.SMTPAuthenticationError as e:
            eb("The server refused your login. Most likely you've mistyped "
               "your username or password, or are trying to log in to the "
               "wrong server. The server told us:\n\n%s" % (e.smtp_error),
               "Incorrect username/password")
        except smtplib.SMTPException as e:
            ui.utils.tracebackBox("The server returned an unexpected error "
                    "that we don't know how to handle. If the error message "
                    "below is not enough to fix the problem, please copy and "
                    "paste the complete error message and contact the "
                    "developer for further assistance.\n\n%s" % (e.smtp_error),
                    includeErrorBoilerplate=False)

    def endOfThread(self):
        self.thread.finished.disconnect() # run end of thread only once
        self.thread.quit()
        self.doClose = True
        self.reject()
        if self.recipientErrors:
            errors = "\n".join([str(i) for i in self.recipientErrors])
            ui.utils.tracebackBox("Some email could not be delivered, probably "
                    "because the email addresses were invalid. All email that "
                    "could be delivered has been delivered. Below is a "
                    "full description of the errors:\n\n%s" % (errors),
                    "Invalid email addresses", includeErrorBoilerplate=False)

    def reject(self):
        if not self.doClose:
            self.thread.exiting = True
            self.form.progressLabel.setText("Canceling...")
        else:
            if self.hadError:
                super(SendingDialog, self).reject()
            else:
                super(SendingDialog, self).accept()


class WorkerThread(QtCore.QThread):
    serverContacted = QtCore.pyqtSignal(name="serverContacted")
    aboutToEmail = QtCore.pyqtSignal(name="aboutToEmail")
    emailFailed = QtCore.pyqtSignal(Exception, list, name="emailFailed")
    recipientRefused = QtCore.pyqtSignal(Exception, name="recipientRefused")

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.SMTPOpen = False
        self.exiting = False
        self.cleanupDone = False

    def tearDown(self):
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
            try:
                self.em.sendEmail(stu)
            except smtplib.SMTPRecipientsRefused as e:
                self.recipientRefused.emit(e)
            except db.emailing.NoResultsError:
                try:
                    self.em.sendEmail(stu, sendNoResultsMessage=True)
                except smtplib.SMTPRecipientsRefused as e:
                    self.recipientRefused.emit(e)

        # done; clean up
        self.tearDown()

    def run(self):
        try:
            self.processEmails()
        except Exception as err:
            # if the destructor is run by another thread, we get an sqlite
            # error, so we need to tear down before we emit the signal
            # TODO: update comment to see if swapping works (otherwise needed)
            #traceback.print_tb(tb)
            ex_type, ex, tb = sys.exc_info()
            self.emailFailed.emit(err, traceback.extract_tb(tb))
            self.tearDown()
