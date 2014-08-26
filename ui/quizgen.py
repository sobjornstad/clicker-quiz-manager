from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QDialog, QMessageBox, QFileDialog
from PyQt4.QtCore import QObject
from forms.quizgen import Ui_Dialog
import forms.qprev

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

        self.form.genButton.clicked.connect(self.onGenerate)
        self.form.cancelButton.clicked.connect(self.reject)
        self.form.setsButton.clicked.connect(self.onSets)
        self.form.setList.itemSelectionChanged.connect(self.onSetChange)
        self.form.classCombo.currentIndexChanged.connect(self.onClassChange)

        self.form.genButton.setEnabled(False)
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
        toggle = [self.form.newSpin, self.form.revSpin, self.form.genButton]
        for i in toggle:
            if self.form.setList.selectedItems():
                i.setEnabled(True)
            else:
                i.setEnabled(False)

    def onGenerate(self):
        sq = self.quiz
        sq.setNewQuestions(self.form.newSpin.value())
        sq.setRevQuestions(self.form.revSpin.value())
        if not self.quiz.isSetUp():
            utils.errorBox("Quiz settings have not been made yet!")
            return

        prevText = self.quiz.generate()
        if not (sq.useNewNum or sq.useRevNum):
            topText = "This quiz is blank. Please add some questions and try again."
        else:
            topText = "This quiz contains %i new questions and %i reviews.\n"
            topText += "New questions are from %s %s."
            sns, n = sq.getSetNames()
            topText = topText % (sq.useNewNum, sq.useRevNum,
                    'the following sets:' if n != 1 else 'the set', sns)

        prevText = '\n\n'.join([topText, prevText])
        d = PreviewDialog(self)
        d.setText(prevText)
        d.exec_()

        if self.quizFilename:
            sq.makeRtfFile(self.quizFilename)
            sq.rewriteSchedule()
            utils.informationBox("The quiz was exported successfully. "
                                 "Sets have been rescheduled.",
                                 "Quiz generated")
            QDialog.accept(self)

    def reject(self):
        QDialog.reject(self)

    def onSets(self):
        import questionsets
        qsw = questionsets.QuestionSetsDialog(self)
        qsw.exec_()

class PreviewDialog(QDialog):
    """
    Displayed to show the user a text version of her quiz and allow her to
    decide whether or not to use it. This should be created as a dialog from
    the generate quiz window.
    """

    def __init__(self, parent=None):
        QDialog.__init__(self)
        self.parent = parent
        self.form = forms.qprev.Ui_Dialog()
        self.form.setupUi(self)

        self.form.okButton.clicked.connect(self.accept)
        self.form.cancelButton.clicked.connect(self.reject)

    def setText(self, txt):
        self.form.prevText.setPlainText(txt)
        if "quiz is blank" in txt:
            self.form.okButton.setEnabled(False)

    def accept(self):
        f = QFileDialog.getSaveFileName(caption="Export Quiz File",
                filter="Rich text files (*.rtf)")
        if not f:
            self.parent.quizFilename = None
            return
        else:
            # on linux, the extension might not be automatically appended
            f = unicode(f)
            if not f.endswith('.rtf'):
                f += '.rtf'
            self.parent.quizFilename = f
            QDialog.accept(self)

    def reject(self):
        self.parent.quizFilename = None
        QDialog.reject(self)
