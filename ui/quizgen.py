from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QDialog, QMessageBox
from PyQt4.QtCore import QObject
from forms.quizgen import Ui_Dialog

import db.classes
import db.genquiz
import db.sets
import db.questions
import utils

class QuizWindow(QDialog):
    def __init__(self, mw):
        QDialog.__init__(self)
        self.mw = mw
        self.form = Ui_Dialog()
        self.form.setupUi(self)

        self.form.okButton.clicked.connect(self.accept)
        self.form.cancelButton.clicked.connect(self.reject)
        self.form.setsButton.clicked.connect(self.onSets)
        self.form.setList.itemSelectionChanged.connect(self.onSetChange)

        self.form.okButton.setEnabled(False)
        self.form.newQuestions.setEnabled(False)
        self.form.revQuestions.setEnabled(False)

        self.setDefaultSpinValues()
        self.populateClasses()
        self.populateSets()
        self.updateDueValues()

    def populateSets(self):
        self.sets = db.genquiz.findNewSets(self.cls)
        for s in self.sets:
            self.form.setList.addItem(s.getName())

    def populateClasses(self):
        self.classes = db.classes.getAllClasses()
        for c in self.classes:
            self.form.classCombo.addItem(c.getName())
        self.onClassChange()

    def updateDueValues(self):
        self.form.reviewDisplay.setText("(%i sets due)" % (5))
        self.form.newDisplay.setText("(%i available)" % (15))

    def setDefaultSpinValues(self):
        self.form.revQuestions.setValue(5)
        newQAvailable = 15
        self.form.newQuestions.setValue(newQAvailable)
        self.form.newQuestions.setMaximum(15)

    def onClassChange(self):
        self.cls = db.classes.getClassByName(
                unicode(self.form.classCombo.currentText()))
        self.quiz = db.genquiz.Quiz(self.cls)

    def onSetChange(self):
        self.onClassChange()
        sq = self.quiz
        sq.resetNewSets()
        for i in self.form.setList.selectedItems():
            sq.addNewSet(db.sets.findSet(name=unicode(i.text())))
        sq.finishSetup()

        revs = sq.getNewAvail()
        news = sq.getRevDue()
        self.form.newQuestions.setValue(news)
        self.form.revQuestions.setValue(revs)

    def setSpinLimits(self):
        pass

    def accept(self):
        QDialog.accept(self)

    def reject(self):
        QDialog.reject(self)

    def onSets(self):
        utils.informationBox("Sets button activated", "Button Clicked")
