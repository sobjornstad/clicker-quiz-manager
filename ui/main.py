# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2014 Soren Bjornstad. All rights reserved.

import os
import traceback
import shutil
import sys

from sqlite3 import OperationalError
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QApplication, QMainWindow, QFileDialog, QDesktopServices, QAction, QInputDialog, QMessageBox
from forms.mw import Ui_MainWindow

import db.database as d
import db.tools.create_database

import ui.classes
import ui.quizgen
import ui.questionsets
import ui.students
import ui.history
import ui.prefs
import ui.utils as utils

APPLICATION_VERSION = "1.0.3"

class MainWindow(QMainWindow):
    def __init__(self):
        # set up main window
        QMainWindow.__init__(self)
        self.form = Ui_MainWindow()
        self.form.setupUi(self)
        self.form.verLabel.setText("Clicker Quiz Manager " + APPLICATION_VERSION)

        # load configuration options
        self.config = ui.prefs.ConfigurationManager()
        self._loadConf()

        # try to open last-used database; if none or doesn't exist, ask user 
        # what file to open
        name = unicode(self.config.readConf('dbPath').toString())
        if (not name) or (not os.path.isfile(name)):
            doWhat = utils.onStartBox()
            if doWhat == 0:
                self.onNewDB()
            elif doWhat == 1:
                # open database
                name = unicode(getDbLocation())
                self._connectDb(name)
            elif doWhat == 2:
                sys.exit(0)
        else:
            self._connectDb(name)

        self.databaseConfig = ui.prefs.DatabaseConfManager(self)

        # connect menus and buttons
        self.form.actionNew.triggered.connect(self.onNewDB)
        self.form.actionOpen.triggered.connect(self.onOpenDB)
        self.form.actionQuit.triggered.connect(self.quit)
        self.form.actionBackup.triggered.connect(self.onBackupDB)
        self.form.actionManual.triggered.connect(self.onManual)
        self.form.actionPreferences.triggered.connect(self.onPrefs)
        self.form.actionVersion.triggered.connect(self.onVersion)
        self.form.actionClear_Saved_Passwords.triggered.connect(self.onClearPW)

        self.form.quitButton.clicked.connect(self.quit)
        self.form.classesButton.clicked.connect(self.onClasses)
        self.form.quizButton.clicked.connect(self.onQuizGen)
        self.form.setsButton.clicked.connect(self.onSets)
        self.form.studentsButton.clicked.connect(self.onStudents)
        self.form.historyButton.clicked.connect(self.onHistory)

    def _connectDb(self, name):
        self.dbpath = name
        d.DatabaseInterface.connectToFile(
                self.dbpath, autosaveInterval=self.autosaveInterval)
        self.dbFilename = self.dbpath.split('/')[-1]
        self.form.dbLabel.setText("Database: " + self.dbFilename)

    def _loadConf(self):
        self.isDebugMode = self.config.readConf("debugMode").toBool()
        if self.isDebugMode:
            self._configureDebugMode()

        self.autoAnsA = self.config.readConf("autoAnsA").toBool()

        autoMins = self.config.readConf("saveInterval").toInt()[0]
        if autoMins == 0:
            self.config.writeConf("saveInterval", 1)
            autoMins = 1
        self.autosaveInterval = autoMins * 60
        # value will be dealt with in _connectDb()

    def onClasses(self):
        cw = ui.classes.ClassesWindow(self)
        cw.exec_()

    def onQuizGen(self):
        if not utils.ensureClassExists():
            utils.errorBox("Please create at least one class first.",
                    "No Classes")
            return False
        qw = ui.quizgen.QuizWindow(self, self.config)
        qw.exec_()

    def onSets(self):
        qsw = ui.questionsets.QuestionSetsDialog(self, self.config)
        qsw.exec_()

    def onStudents(self):
        stw = ui.students.StudentsDialog(self)
        stw.exec_()

    def onHistory(self):
        hiw = ui.history.HistoryDialog(self, self.databaseConfig, self.config)
        hiw.exec_()

    def closeEvent(self, event):
        self.quit()

    def quit(self):
        # save current database location to configuration
        self.config.writeConf('dbPath', self.dbpath)
        self.config.sync()
        self.databaseConfig.sync()
        d.inter.close()
        sys.exit(0)

    def onNewDB(self):
        fname = QFileDialog.getSaveFileName(caption="Create New Database",
                filter="Quiz Databases (*.db);;All files (*)")
        fname = unicode(fname)
        if not fname: # canceled
            return
        fname = utils.forceExtension(fname, 'db')
        if fname is None:
            # see docstring of forceExtension
            return

        if db.database.inter is not None: # could be no db open yet
            db.database.inter.close()
        # trying to create over an existing db causes lots of errors
        try:
            os.remove(fname)
        except OSError:
            pass
        connection = db.tools.create_database.makeDatabase(fname)
        connection.close()
        self._connectDb(fname)

    def onOpenDB(self):
        db.database.inter.close()
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
        copyto = utils.forceExtension(copyto, 'db')
        if copyto is None:
            # see docstring of forceExtension
            return
        db.database.inter.close() # make sure everything's been saved
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
        if os.path.isfile(manualLoc):
            QDesktopServices.openUrl(QtCore.QUrl(manualLoc))
        else:
            utils.errorBox("Could not locate the manual! Please report this " \
                           "error to the developer.", "File not found")

    def onPrefs(self):
        pw = ui.prefs.PrefsDialog(self)
        pw.exec_()

    def onVersion(self):
        utils.informationBox(APPLICATION_VERSION, "Version")

    def onClearPW(self):
        r = utils.questionBox("Do you really want to clear all saved email "
                              "passwords for all classes?", "Clear passwords?")
        if r == QMessageBox.Yes:
            ui.prefs.wipeAllPasswords(self.databaseConfig)
        utils.informationBox("All saved passwords have been cleared.", "Success")

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

        def forceSave():
            db.database.forceSave()
            utils.informationBox("Saved.")
        actionForceSave = QAction(self)
        actionForceSave.setText("Force save now")
        debugMenu.addAction(actionForceSave)
        actionForceSave.triggered.connect(forceSave)


    def exception_hook(self, exctype, value, tb):
        tbtext = ''.join(traceback.format_exception(exctype, value, tb))
        utils.tracebackBox(tbtext, isDebug=self.isDebugMode)
        return


def start():
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_X11InitThreads)
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
