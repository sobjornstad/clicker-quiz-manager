from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QDialog, QMessageBox, QInputDialog, QPlainTextEdit, QComboBox
from forms.editset import Ui_Dialog

import utils
from db.sets import getAllSets

class CorrectAnswersComboBox(QComboBox):
    def focusInEvent(self, event):
        self.window().populateCorrectAnswer()

class SetEditor(QDialog):
    def __init__(self, setList):
        QDialog.__init__(self)
        self.sl = setList
        self.form = Ui_Dialog()
        self.form.setupUi(self)

        self.populateSets()

        self.form.newButton.clicked.connect(self.onNew)
        self.form.deleteButton.clicked.connect(self.onDelete)
        self.form.importButton.clicked.connect(self.onImport)
        self.form.exportButton.clicked.connect(self.onExport)
        self.form.moveDownButton.clicked.connect(self.onMoveDown)
        self.form.moveUpButton.clicked.connect(self.onMoveUp)
        self.form.saveButton.clicked.connect(self.onSaveQuestion)
        self.form.closeButton.clicked.connect(self.accept)

    def populateSets(self):
        self.l = getAllSets()
        for s in self.l:
            self.form.jumpCombo.addItem(s.getName())

        # select the set we're editing from it
        txt = self.sl.form.setList.currentItem().text()
        i = self.form.jumpCombo.findText(txt)
        self.form.jumpCombo.setCurrentIndex(i)

    def onNew(self):
        nqText = "New Question"
        self.form.questionList.addItem(nqText)
        newRow = self.form.questionList.count() - 1
        self.form.questionList.setCurrentRow(newRow)
        self.form.questionBox.setPlainText(nqText)
        self.form.questionBox.setFocus()
        self.form.questionBox.selectAll()
        self.form.questionBox.textChanged.connect(self.updateListQuestion)

    def populateCorrectAnswer(self):
        """Called when focusing the 'correct answer' box to figure out what
        should go in there."""

        # save user's current choice, if any
        pass

        # empty existing choices, if any
        self.form.correctAnswerCombo.clear()

        # fill with new set of choices
        sf = self.form
        aBoxes = [sf.answerA, sf.answerB, sf.answerC, sf.answerD, sf.answerE]
        aNames = {sf.answerA: 'A', sf.answerB: 'B', sf.answerC: 'C',
                sf.answerD: 'D', sf.answerE: 'E'}
        for ans in aBoxes:
            if ans.text() != '':
                print "adding ans %r" % aNames[ans]
                self.form.correctAnswerCombo.addItem(aNames[ans], 0)
            else:
                # that was the last answer choice; we don't want to allow, say,
                # 'A', 'B', and 'D' as options
                break

    def updateListQuestion(self):
        """Called when editing the question, to keep the question's entry in the
        list in sync."""

        txt = unicode(self.form.questionBox.toPlainText())
        self.form.questionList.currentItem().setData(0, txt)

    def onSaveQuestion(self):
        """Called when clicking the "save changes" button, or hopefully
        eventually when question editing section of the dialog loses focus."""
        pass

    def onDelete(self):
        pass

    def onImport(self):
        utils.informationBox("This feature is not implemented yet.", "Sorry!")

    def onExport(self):
        utils.informationBox("This feature is not implemented yet.", "Sorry!")

    def onMoveDown(self):
        pass

    def onMoveUp(self):
        pass
