# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2015 Soren Bjornstad. All rights reserved.

from copy import deepcopy

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QDialog, QInputDialog, QMessageBox, QShortcut, \
     QKeySequence, QFileDialog, QLineEdit
from PyQt4.QtCore import QObject
from ui.forms.emailopts import Ui_Dialog

import ui.sendingmail
import ui.utils as utils
from db.history import HistoryItem

class PasswordSafeQLineEdit(QLineEdit):
    # NOTE: This doesn't disable undo from the context menu, which is also
    # necessary for this to be "password-safe." This is done in the dialog by
    # creating a custom context menu and using the displayContextMenu()
    # function.
    def keyPressEvent(self,event):
        if event.key()==(QtCore.Qt.Key_Control and QtCore.Qt.Key_Z):
            self.undo()
        else:
            QLineEdit.keyPressEvent(self,event)

    def undo(self):
        pass

class EmailingDialog(QDialog):
    def __init__(self, parent, cls, zid, dbConf, qConf):
        QDialog.__init__(self)
        self.form = Ui_Dialog()
        self.form.setupUi(self)
        self.cls = cls
        self.zid = zid
        self.dbConf = dbConf
        self.qConf = qConf

        self.setWindowTitle("Email Results ~ Quiz %i, %s" % (
            HistoryItem(zid).seq, self.cls.getName()))
        self.form.SSLCombo.addItems(["None", "SSL/TLS", "STARTTLS"])

        self.form.cancelButton.clicked.connect(self.reject)
        self.form.sendMailButton.clicked.connect(self.onSendMail)
        #self.form.sendTestButton.clicked.connect(self.onSendTest)
        self.form.showPWCheck.toggled.connect(self.toggleShowPW)
        self.form.passwordBox.textEdited.connect(self.unsetPasswordWasLoaded)
        self.form.passwordBox.customContextMenuRequested.connect(
                self.displayPasswordContextMenu)

        self.fetchOptions()
        self.makeOptionsDict()

    def fetchOptions(self):
        key = 'optionsForClass_' + self.cls.getName()
        opts = self.dbConf.get(key)

        if opts is not None:
            self.form.fromNameBox.setText(opts['fromName'])
            self.form.fromAddrBox.setText(opts['fromAddr'])
            self.form.subjectBox.setText(opts['subject'])
            self.form.bodyBox.setPlainText(opts['body'])
            self.form.hostnameBox.setText(opts['hostname'])
            self.form.portBox.setText(opts['port'])
            comboIndex = self.form.SSLCombo.findText(opts['ssl'])
            self.form.SSLCombo.setCurrentIndex(comboIndex)
            self.form.usernameBox.setText(opts['username'])
            self.form.passwordBox.setText(opts['password'])
            self.passwordWasLoaded = True if opts['password'] else False
        else:
            self.passwordWasLoaded = False

    def makeOptionsDict(self):
        opts = {}
        opts['fromName'] = unicode(self.form.fromNameBox.text())
        opts['fromAddr'] = unicode(self.form.fromAddrBox.text())
        opts['subject'] = unicode(self.form.subjectBox.text())
        opts['body'] = unicode(self.form.bodyBox.toPlainText())
        opts['hostname'] = unicode(self.form.hostnameBox.text())
        opts['port'] = unicode(self.form.portBox.text())
        opts['ssl'] = unicode(self.form.SSLCombo.currentText())
        opts['username'] = unicode(self.form.usernameBox.text())
        opts['password'] = unicode(self.form.passwordBox.text())
        self.opts = opts

    def putOptions(self):
        self.makeOptionsDict()
        opts = deepcopy(self.opts)
        if not self.qConf.readConf('savePasswords').toBool():
            opts['password'] = ''
        key = 'optionsForClass_' + self.cls.getName()
        self.dbConf.put(key, opts)
        self.dbConf.sync()
        #TODO: preview options

    def toggleShowPW(self):
        doShow = self.form.showPWCheck.isChecked()
        if doShow:
            # if password was saved in the config, don't let it be shown in
            # plaintext for some basic security
            if self.passwordWasLoaded:
                r = utils.questionBox("For security reasons, you cannot view "
                        "any part of a saved password. Would you like to erase "
                        "the saved password?", "Erase Password")
                if r == QMessageBox.Yes:
                    self.form.passwordBox.setText("")
                    self.passwordWasLoaded = False
                else:
                    self.form.showPWCheck.setChecked(False)
                    return
            self.form.passwordBox.setEchoMode(QLineEdit.Normal)
        else:
            self.form.passwordBox.setEchoMode(QLineEdit.Password)

    def unsetPasswordWasLoaded(self):
        if unicode(self.form.passwordBox.text()) == '':
            self.passwordWasLoaded = False

    def displayPasswordContextMenu(self, point):
        menu = self.form.passwordBox.createStandardContextMenu()
        for action in menu.actions():
            if action.text() == '&Undo\tCtrl+Z':
                action.setDisabled(True)
                break
        menu.exec_(self.form.passwordBox.mapToGlobal(point))

    def onSendMail(self):
        # have an option to preview the email
        self.form.showPWCheck.setChecked(False) # don't show pw while running
        self.makeOptionsDict()
        self.putOptions()
        busyDialog = ui.sendingmail.SendingDialog(
                self, self.opts, self.cls, self.zid)
        sendWasSuccessful = busyDialog.exec_()
        if sendWasSuccessful:
            self.accept()

    def onSendTest(self):
        pass
