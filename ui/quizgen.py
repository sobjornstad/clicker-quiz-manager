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
        self.form.classCombo.currentIndexChanged.connect(self.onClassChange)

        self.form.okButton.setEnabled(False)
        self.form.newSpin.setEnabled(False)
        self.form.revSpin.setEnabled(False)

        self.setDefaultSpinValues()
        self.populateClasses()
        self.updateDueValues(0, 0)

    def populateSets(self):
        self.form.setList.clear()
        self.sets = db.genquiz.findNewSets(self.cls)
        for s in self.sets:
            self.form.setList.addItem(s.getName())

    def populateClasses(self):
        self.classes = db.classes.getAllClasses()
        for c in self.classes:
            self.form.classCombo.addItem(c.getName())
        self.onClassChange()

    def updateDueValues(self, news, revs):
        self.form.newDisplay.setText("(%i available)" % (news))
        self.form.reviewDisplay.setText("(%i sets due)" % (revs))

    def setDefaultSpinValues(self):
        for i in [self.form.revSpin, self.form.newSpin]:
            i.setValue(0)
            i.setMaximum(0)
            i.setMinimum(0)

    def onClassChange(self):
        self.cls = db.classes.getClassByName(
                unicode(self.form.classCombo.currentText()))
        self.quiz = db.genquiz.Quiz(self.cls)
        self.populateSets()

    def onSetChange(self):
        sq = self.quiz
        sq.resetNewSets()
        for i in self.form.setList.selectedItems():
            sq.addNewSet(db.sets.findSet(name=unicode(i.text())))
        sq.finishSetup()

        news = sq.getNewAvail()
        revs = sq.getRevDue()
        self.updateDueValues(news, revs)
        self.form.newSpin.setMaximum(news)
        self.form.revSpin.setMaximum(revs)

        # update grayed-out parts of dialog
        toggle = [self.form.newSpin, self.form.revSpin, self.form.okButton]
        for i in toggle:
            if self.form.setList.selectedItems():
                i.setEnabled(True)
            else:
                i.setEnabled(False)

    def accept(self):
        QDialog.accept(self)

    def reject(self):
        QDialog.reject(self)

    def onSets(self):
        import questionsets
        qsw = questionsets.QuestionSetsDialog(self)
        qsw.exec_()
