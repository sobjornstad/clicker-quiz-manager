# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2014 Soren Bjornstad. All rights reserved.

import sys

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QApplication, QMainWindow, QFileDialog
from forms.mw import Ui_MainWindow
import utils

import db.database

APPLICATION_VERSION = "1.0.0"

class MainWindow(QMainWindow):
    def __init__(self):
        self.dbpath = unicode(getDbLocation())
        db.database.connect(self.dbpath)
        QMainWindow.__init__(self)
        self.form = Ui_MainWindow()
        self.form.setupUi(self)
        self.config = ConfigurationManager()

        filename = self.dbpath.split('/')[-1]
        self.form.dbLabel.setText("Database: " + filename)
        self.form.verLabel.setText("Clicker Quiz Manager " + APPLICATION_VERSION)

        self.form.quitButton.clicked.connect(self.quit)
        self.form.classesButton.clicked.connect(self.onClasses)
        self.form.quizButton.clicked.connect(self.onQuizGen)
        self.form.setsButton.clicked.connect(self.onSets)

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
        db.database.close()
        sys.exit(0)

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
