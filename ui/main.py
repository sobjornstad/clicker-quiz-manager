# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2014 Soren Bjornstad. All rights reserved.

import os, sys

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QApplication, QMainWindow, QFileDialog, QDesktopServices, QAction, QInputDialog
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

        # load configuration options
        self.config = ConfigurationManager()
        self.isDebugMode = self.config.readConf("debugMode").toBool()
        if self.isDebugMode:
            self._configureDebugMode()

        autoMins = self.config.readConf("saveInterval").toInt()[0]
        if autoMins == 0:
            self.config.writeConf("saveInterval", 1)
            autoMins = 1
        self.autosaveInterval = autoMins * 60
        # value will be dealt with in _connectDb()

        # try to open last-used database; if none or doesn't exist, ask user 
        # what file to open
        name = unicode(self.config.readConf('dbPath').toString())
        if (not name) or (not os.path.isfile(name)):
            name = unicode(getDbLocation())
        self._connectDb(name)

        # connect menus and buttons
        self.form.actionNew.triggered.connect(self.onNewDB)
        self.form.actionOpen.triggered.connect(self.onOpenDB)
        self.form.actionQuit.triggered.connect(self.quit)
        self.form.actionBackup.triggered.connect(self.onBackupDB)
        self.form.actionManual.triggered.connect(self.onManual)
        self.form.actionPreferences.triggered.connect(self.onPrefs)
        self.form.actionVersion.triggered.connect(self.onVersion)

        self.form.quitButton.clicked.connect(self.quit)
        self.form.classesButton.clicked.connect(self.onClasses)
        self.form.quizButton.clicked.connect(self.onQuizGen)
        self.form.setsButton.clicked.connect(self.onSets)

    def _connectDb(self, name):
        self.dbpath = name
        db.database.connect(self.dbpath, autosaveInterval=self.autosaveInterval)
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
        self.config.writeConf('dbPath', self.dbpath)
        db.database.close()
        sys.exit(0)

    def onNewDB(self):
        fname = QFileDialog.getSaveFileName(caption="Create New Database",
                filter="Quiz Databases (*.db);;All files (*)")
        fname = unicode(fname)
        if not fname: # canceled
            self._connectDb(self.dbpath)
            return
        connection = db.tools.create_database.makeDatabase(fname)
        connection.close()
        self._connectDb(fname)

    def onOpenDB(self):
        db.database.close()
        name = unicode(getDbLocation())
        if not name:
            self._connectDb(self.dbpath)
            return
        self._connectDb(name)

    def onBackupDB(self):
        copyto = QFileDialog.getSaveFileName(caption="Save Backup As",
                filter="Quiz Databases (*.db);;All files (*)")
        copyto = unicode(copyto)
        if not copyto: # canceled
            return
        db.database.close() # make sure everything's been saved & taken care of
        import shutil
        try:
            shutil.copyfile(self.dbpath, copyto)
        except shutil.Error:
            utils.errorBox("You cannot back up a file to itself! " \
                           "(But nice try...)", "Backup failed")
        except IOError:
            utils.errorBox("Backup failed. Please be sure that the " \
                           "destination is writeable and not full and " \
                           "that you have permission to access it.",
                           "Backup failed")
        else:
            utils.informationBox("Backup successful.", "Success")
        finally:
            self._connectDb(self.dbpath) # reconnect

    def onManual(self):
        manualLoc = "docs/manual.html"
        if os.path.isfile(floc):
            QDesktopServices.openUrl(QtCore.QUrl(manualLoc))
        else:
            utils.errorBox("Could not locate the manual! Please report this " \
                           "error to the developer.", "File not found")

    def onPrefs(self):
        import prefs
        pw = prefs.PrefsDialog(self)
        pw.exec_()

    def onVersion(self):
        utils.informationBox(APPLICATION_VERSION, "Version")

    def _configureDebugMode(self):
        debugMenu = self.form.menuBar.addMenu('&Debug');

        def throwError():
            5/0
        actionThrowError = QAction(self)
        #actionThrowError.setObjectName("actionThrowError")
        actionThrowError.setText("Throw Exception")
        debugMenu.addAction(actionThrowError)
        actionThrowError.triggered.connect(throwError)

        def showConfigurations():
            keys = self.config.allKeys()
            strRep = ""
            for i in keys:
                strRep += i + ":\t" + self.config.readConf(i).toString() + '\n'
            utils.tracebackBox(strRep, "Config Options", False)
        actionShowConf = QAction(self)
        actionShowConf.setText("Show Configuration...")
        debugMenu.addAction(actionShowConf)
        actionShowConf.triggered.connect(showConfigurations)

        def writeConfiguration():
            key, ok = QInputDialog.getText(self, "Write Config Value", "Key:")
            if (not ok) or (not key):
                utils.informationBox("Cancelled.")
                return
            value, ok = QInputDialog.getText(self, "Write Config Value", "Value:")
            if (not ok) or (not value):
                utils.informationBox("Cancelled.")
                return
            self.config.writeConf(key, value)
        actionWriteConf = QAction(self)
        actionWriteConf.setText("Write Configuration Value...")
        debugMenu.addAction(actionWriteConf)
        actionWriteConf.triggered.connect(writeConfiguration)



    def exception_hook(self, exctype, value, tb):
        import traceback
        tbtext = ''.join(traceback.format_exception(exctype, value, tb))
        utils.tracebackBox(tbtext, isDebug=self.isDebugMode)
        return

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

    def allKeys(self):
        "Return Python list of all keys in existence."
        keys = self.qs.allKeys()
        return [str(i) for i in keys]


def start():
    app = QApplication(sys.argv)
    mw = MainWindow()
    sys._excepthook = sys.excepthook
    sys.excepthook = mw.exception_hook
    mw.show()
    app.exec_()

def getDbLocation():
    # self.dbpath = unicode(getDbLocation())
    f = QFileDialog.getOpenFileName(caption="Open Database",
            filter="Quiz Databases (*.db);;All files (*)")
    return f
