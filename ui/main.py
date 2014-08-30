# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2014 Soren Bjornstad. All rights reserved.

import sys

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QApplication, QMainWindow, QFileDialog
from forms.mw import Ui_MainWindow

import db.database

APPLICATION_VERSION = "1.0.0"

class MainWindow(QMainWindow):
    def __init__(self):
        self.dbpath = unicode(getDbLocation())
        db.database.connect(self.dbpath)
        QMainWindow.__init__(self)
        self.form = Ui_MainWindow()
        self.form.setupUi(self)

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

def start():
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    app.exec_()

def getDbLocation():
    f = QFileDialog.getOpenFileName(caption="Open Database",
            filter="Quiz Databases (*.db);;All files (*)")
    return f
