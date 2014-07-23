import sys
#sys.path.append("../")

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QApplication, QMainWindow
from forms.mw import Ui_MainWindow

import db.database

class MainWindow(QMainWindow):
    def __init__(self):
        db.database.connect("quiz.db")
        QMainWindow.__init__(self)
        self.form = Ui_MainWindow()
        self.form.setupUi(self)

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
