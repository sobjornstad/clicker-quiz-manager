# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2014 Soren Bjornstad. All rights reserved.

import os

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QDialog, QMessageBox
from PyQt4.QtCore import QObject
from forms.exception import Ui_Dialog
import forms.busy

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

def warningBox(text, title=None):
    msgBox = QMessageBox()
    msgBox.setText(text)
    msgBox.setIcon(QMessageBox.Warning)
    if title:
        msgBox.setWindowTitle(title)
    msgBox.exec_()

def questionBox(text, title=None):
    msgBox = QMessageBox()
    msgBox.setText(text)
    msgBox.setIcon(QMessageBox.Question)
    msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msgBox.setDefaultButton(QMessageBox.No)
    if title:
        msgBox.setWindowTitle(title)
    return msgBox.exec_()

def onStartBox():
    text = "Welcome to the Clicker Quiz Manager! Either you've"\
           " never opened a database on this computer or your database"\
           " has been moved since you last used CQM. What would you"\
           " like to do?"
    title = "Database not found"
    msgBox = QMessageBox()
    msgBox.setText(text)
    msgBox.setIcon(QMessageBox.Question)
    defaultButton = msgBox.addButton("&Create new database", QMessageBox.YesRole)
    msgBox.addButton("&Open existing database", QMessageBox.NoRole)
    msgBox.addButton("&Quit", QMessageBox.RejectRole)
    msgBox.setDefaultButton(defaultButton)
    msgBox.setWindowTitle(title)
    return msgBox.exec_()

def confirmDeleteBox(item, additional=''):
    msgBox = QMessageBox()
    s = "Are you sure you want to delete this %s? %s" % (item, additional)
    msgBox.setText(s)
    msgBox.setIcon(QMessageBox.Question)
    msgBox.setWindowTitle("Delete %s" % item.title())
    msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msgBox.setDefaultButton(QMessageBox.No)
    return msgBox.exec_()

def forceExtension(filename, ext):
    """
    On Linux, a filename extension might not be automatically appended to the
    result of a file open/save box. This means we have to do it ourselves and
    check to be sure we're not overwriting something ourselves.

    This check is not safe from race conditions (if another program wrote a
    file with the same name between this function running and the output
    routine, the other file would be overwritten), but the chance of that
    causing a bad problem are essentially zero in this situation, and
    neither is the normal file-save routine.

    Arguments:
        filename: the path to (or simple name of) the file we're checking
        ext: the extension, without period, you want to ensure is included

    Return:
      - The filename (modified or not) if the file does not exist;
      - None if it does exist and the user said she didn't want to
        overwrite it.
    """
    # on linux, the extension might not be automatically appended
    filename = unicode(filename)
    if not filename.endswith('.%s' % ext):
        filename += ".%s" % ext
        if os.path.exists(filename):
            r = questionBox("%s already exists.\nDo you want to "
                            "replace it?" % filename)
            if r != QMessageBox.Yes: # yes
                return None
    return filename



#class BusyDialog(QDialog):
    #"""
    #A dialog showing the busy/bouncing progress bar.
    #"""
    #def __init__(self, parent):
        #QDialog.__init__(self)
        #self.form = forms.busy.Ui_Dialog()
        #self.form.setupUi(self)

nodebugErrorText = """
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

debugErrorText = """
Oops! An error occurred that CQM doesn't know how to
deal with. It may be a harmless bug, or it may indicate
a problem with your database or a larger bug in the
operation you're trying to do.

Please report this error to the developer, copying and
pasting the following error information, so that the
bug can be corrected or an appropriate error message
created:
""".strip()

class ErrorBoxWindow(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.form = Ui_Dialog()
        self.form.setupUi(self)
        self.form.okButton.clicked.connect(self.reject)

    def setErrorText(self, text, includeErrorBoilerplate=True, debug=False):
        if includeErrorBoilerplate:
            if debug:
                tbtext = debugErrorText
            else:
                tbtext = nodebugErrorText
            tbtext += '\n\n'
        else:
            tbtext = ""

        tbtext += text
        self.form.text.setPlainText(tbtext)

    def setErrorTitle(self, title):
        self.setWindowTitle(title)

def tracebackBox(text, title=None, includeErrorBoilerplate=True, isDebug=False):
    tbw = ErrorBoxWindow()
    tbw.setErrorText(text, includeErrorBoilerplate, isDebug)
    if title:
        tbw.setErrorTitle(title)
    tbw.exec_()

def ensureClassExists():
    import db.classes
    classes = db.classes.getAllClasses()
    return True if len(classes) >= 1 else False
