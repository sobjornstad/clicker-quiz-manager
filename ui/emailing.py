# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2015 Soren Bjornstad. All rights reserved.

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QDialog, QInputDialog, QMessageBox, QShortcut, \
     QKeySequence, QFileDialog, QLineEdit
from PyQt4.QtCore import QObject
from ui.forms.emailopts import Ui_Dialog

import ui.utils as utils
from db.history import HistoryItem

class PasswordSafeQLineEdit(QLineEdit):
    # NOTE: This doesn't disable the undo from the context menu; for this to be
    # safe, it's currently necessary to disable the context menu. See
    # http://stackoverflow.com/questions/31929996/
    # prevent-undo-in-a-particular-text-box
    def keyPressEvent(self,event):
        if event.key()==(QtCore.Qt.Key_Control and QtCore.Qt.Key_Z):
            self.undo()
        else:
            QLineEdit.keyPressEvent(self,event)

    def undo(self):
        pass

class EmailingDialog(QDialog):
    def __init__(self, parent, cls, zid):
        QDialog.__init__(self)
        self.form = Ui_Dialog()
        self.form.setupUi(self)
        self.cls = cls
        self.zid = zid

        self.setWindowTitle("Email Results ~ Quiz %i, %s" % (
            HistoryItem(zid).seq, self.cls.getName()))
        self.form.SSLCombo.addItems(["None", "SSL/TLS", "STARTTLS"])

        self.form.cancelButton.clicked.connect(self.reject)
        self.form.showPWCheck.toggled.connect(self.toggleShowPW)
        self.form.passwordBox.textEdited.connect(self.unsetPasswordWasLoaded)

        self.fetchOptions()
        self.makeOptionsDict()

    def fetchOptions(self):
        # do something to get the options from the conf part of the db; for now,
        # we just have them hard-coded as a sample
        opts = {'fromName': 'Soren Bjornstad',
                'fromAddr': 'redacted@example.com',
                'subject': '[CQM $c] Results for Quiz $n',
                'body': 'This is a test. Here are your results:\n$Q',
                'hostname': 'mail.messagingengine.com',
                'port': '465',
                'ssl': 'SSL/TLS',
                'username': 'redacted@fastmail.com',
                'password': 'notReallyMyPassword'
               }

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
        return opts

    def putOptions(self):
        # do something to save the options into the db; for now, we do nothing.
        pass

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
