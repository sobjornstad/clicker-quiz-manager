# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2014 Soren Bjornstad. All rights reserved.

import os, sys

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QApplication, QMainWindow, QFileDialog, QDesktopServices
from forms.mw import Ui_MainWindow
import utils

import db.database
import db.tools.create_database

APPLICATION_VERSION = "1.0.0"

class MainWindow(QMainWindow):
    def __init__(self):
        # set up main window
        QMainWindow.__init__(self)
        self.form = Ui_MainWindow()
        self.form.setupUi(self)
        self.form.verLabel.setText("Clicker Quiz Manager " + APPLICATION_VERSION)

        # try to open last-used database; if none or doesn't exist, ask user 
        # what file to open
        self.config = ConfigurationManager()
        name = unicode(self.config.readConf('dbFilename').toString())
        if (not name) or (not os.path.isfile(name)):
            name = unicode(getDbLocation())
        self._connectDb(name)

        self.form.actionNew.triggered.connect(self.onNewDB)
        self.form.actionOpen.triggered.connect(self.onOpenDB)
        self.form.actionQuit.triggered.connect(self.quit)
        self.form.actionBackup.triggered.connect(self.onBackupDB)
        self.form.actionManual.triggered.connect(self.onManual)
        self.form.actionPreferences.triggered.connect(self.onPrefs)

        self.form.quitButton.clicked.connect(self.quit)
        self.form.classesButton.clicked.connect(self.onClasses)
        self.form.quizButton.clicked.connect(self.onQuizGen)
        self.form.setsButton.clicked.connect(self.onSets)

    def _connectDb(self, name):
        self.dbpath = name
        db.database.connect(self.dbpath)
        self.dbFilename = self.dbpath.split('/')[-1]
        self.form.dbLabel.setText("Database: " + self.dbFilename)

    def onClasses(self):
        import classes
        cw = classes.ClassesWindow(self)
        cw.exec_()

    def onQuizGen(self):
        import quizgen
        qw = quizgen.QuizWindow(self)
        qw.exec_()

    def onSets(self):
        import questionsets
        qsw = questionsets.QuestionSetsDialog(self)
        qsw.exec_()

    def quit(self):
        # save current database location to configuration
        self.config.writeConf('dbFilename', self.dbFilename)
        db.database.close()
        sys.exit(0)

    def onNewDB(self):
        fname = QFileDialog.getSaveFileName(caption="Create New Database",
                filter="Quiz Databases (*.db);;All files (*)")
        fname = unicode(fname)
        connection = db.tools.create_database.makeDatabase(fname)
        connection.close()
        self._connectDb(fname)

    def onOpenDB(self):
        db.database.close()
        name = unicode(getDbLocation())
        self._connectDb(name)

    def onBackupDB(self):
        pass
    def onManual(self):
        manualLoc = "docs/manual.html"
        if os.path.isfile(floc):
            QDesktopServices.openUrl(QtCore.QUrl(manualLoc))
        else:
            utils.errorBox("Could not locate the manual! Please report this " \
                           "error to the developer.", "File not found")

    def onPrefs(self):
        pass

class ConfigurationManager(object):
    def __init__(self):
        self.qs = QtCore.QSettings("562 Software", "CQM")

    def writeConf(self, key, value):
        "Write a *value* to the persistent config under key *key*."
        self.qs.setValue(key, value)
    def readConf(self, key):
        """
        Return a value from the persistent config stored under key *key*. In
        order to use the value usefully, you need to call its .toInt() or
        .toString() method (other conversions are available where appropriate --
        see docs or do dir(returnval)).

        If the key does not exist, a value of 0 or an empty string will be
        returned, respectively; keep that in mind when designing the values.
        """
        return self.qs.value(key)


def start():
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    app.exec_()

def getDbLocation():
    # self.dbpath = unicode(getDbLocation())
    f = QFileDialog.getOpenFileName(caption="Open Database",
            filter="Quiz Databases (*.db);;All files (*)")
    return f

sys._excepthook = sys.excepthook
def exception_hook(exctype, value, tb):
    import traceback
    tbtext = ''.join(traceback.format_exception(exctype, value, tb))
    utils.tracebackBox(tbtext)
    return
sys.excepthook = exception_hook
