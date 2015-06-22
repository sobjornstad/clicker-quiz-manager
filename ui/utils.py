# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2014 Soren Bjornstad. All rights reserved.

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QDialog, QMessageBox
from PyQt4.QtCore import QObject
from forms.exception import Ui_Dialog

def informationBox(text, title=None):
    msgBox = QMessageBox()
    msgBox.setText(text)
    msgBox.setIcon(QMessageBox.Information)
    if title:
        msgBox.setWindowTitle(title)
    msgBox.exec_()

def errorBox(text, title=None):
    msgBox = QMessageBox()
    msgBox.setText(text)
    msgBox.setIcon(QMessageBox.Critical)
    if title:
        msgBox.setWindowTitle(title)
    msgBox.exec_()

def questionBox(text, title=None):
    msgBox = QMessageBox()
    msgBox.setText(text)
    msgBox.setIcon(QMessageBox.Question)
    if title:
        msgBox.setWindowTitle(title)
    return msgBox.exec_()

def confirmDeleteBox(item, additional):
    msgBox = QMessageBox()
    s = "Are you sure you want to delete this %s? %s" % (item, additional)
    msgBox.setText(s)
    msgBox.setIcon(QMessageBox.Question)
    msgBox.setWindowTitle("Delete %s" % item.title())
    msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msgBox.setDefaultButton(QMessageBox.No)
    return msgBox.exec_()

class ErrorBoxWindow(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.form = Ui_Dialog()
        self.form.setupUi(self)
        self.form.okButton.clicked.connect(self.reject)

    def setErrorText(self, text, includeErrorBoilerplate=True):
        if includeErrorBoilerplate:
            tbtext = """
Oops! An error occurred that CQM doesn't know how to
deal with. It may be a harmless bug, or it may indicate
a problem with your database or a larger bug in the
operation you're trying to do.

Try restarting the program and resuming your work; if
problems continue, please copy and paste the following
error information into support correspondence, along
with information about what you were trying to do when
the error occurred:
            """.strip()

            tbtext += '\n\n'
        else:
            tbtext = ""

        tbtext += text
        self.form.text.setPlainText(tbtext)

    def setErrorTitle(self, title):
        self.setWindowTitle(title)

def tracebackBox(text, title=None, includeErrorBoilerplate=True):
    tbw = ErrorBoxWindow()
    tbw.setErrorText(text, includeErrorBoilerplate)
    if title:
        tbw.setErrorTitle(title)
    tbw.exec_()
