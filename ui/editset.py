# -*- encoding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QDialog, QMessageBox, QInputDialog, QPlainTextEdit, QComboBox
from forms.editset import Ui_Dialog

import utils
from db.sets import getAllSets
from db.questions import Question, QuestionFormatError
import db.sets, db.questions

class SetEditor(QDialog):
    def __init__(self, setList):
        QDialog.__init__(self)
        self.sl = setList
        self.form = Ui_Dialog()
        self.form.setupUi(self)

        self.populateSets()
        self.populateQuestions()
        self.populateCorrectAnswer()

        self.form.correctAnswerCombo.activated.connect(self.onCorrectAnswerChoice)
        self.form.questionList.itemSelectionChanged.connect(self.onQuestionChange)

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
        set = self.sl.form.setList.currentItem().text()
        i = self.form.jumpCombo.findText(set)
        self.form.jumpCombo.setCurrentIndex(i)

    def populateQuestions(self):
        "Fill list box with existing questions in the set."

        questions = db.questions.getBySet(self._currentSet())
        for i in questions:
            self.form.questionList.addItem(i.getQuestion())

    def populateCorrectAnswer(self):
        """Fill correct answer box with A-E. It would be ideal to only fill the
        ones that the user had selected, but we appear to have run into Qt bugs
        there: http://goo.gl/mQ1b83"""

        self.form.correctAnswerCombo.addItem("", 0) # no choice selected yet
        for ans in ['A', 'B', 'C', 'D', 'E']:
            self.form.correctAnswerCombo.addItem(ans, 0)

    def onCorrectAnswerChoice(self):
        i = self.form.correctAnswerCombo.findText("")
        self.form.correctAnswerCombo.removeItem(i)

    def onQuestionChange(self):
        q = db.questions.getByName(
            unicode(self.form.questionList.currentItem().text()))
        if not q:
            print "no q"
            return

        sf = self.form
        ansChoices = [sf.answerA, sf.answerB, sf.answerC, sf.answerD, sf.answerE]
        a = q.getAnswersList()
        for i in range(len(a)):
            ansChoices[i].setText(a[i])

        i = Question._qLetters.index(q.getCorrectAnswer())
        sf.correctAnswerCombo.setCurrentIndex(i)

    def onNew(self):
        nqText = "New Question"
        self.form.questionList.addItem(nqText)
        newRow = self.form.questionList.count() - 1
        self.form.questionList.setCurrentRow(newRow)
        self.form.questionBox.setPlainText(nqText)
        self.form.questionBox.setFocus()
        self.form.questionBox.selectAll()
        self.form.questionBox.textChanged.connect(self.updateListQuestion)

    def updateListQuestion(self):
        """Called when editing the question, to keep the question's entry in the
        list in sync."""

        txt = unicode(self.form.questionBox.toPlainText())
        self.form.questionList.currentItem().setData(0, txt)

    def onSaveQuestion(self):
        """Called when clicking the "save changes" button, or hopefully
        eventually when question editing section of the dialog loses focus."""

        def saveError(msg):
            deferror = "The question you provided is invalid: %s." % msg
            utils.errorBox(deferror, "Save Error")

        sf = self.form
        ansChoices = [sf.answerA, sf.answerB, sf.answerC, sf.answerD, sf.answerE]
        ansDict = {'a': unicode(ansChoices[0].text()),
                   'b': unicode(ansChoices[1].text()),
                   'c': unicode(ansChoices[2].text()),
                   'd': unicode(ansChoices[3].text()),
                   'e': unicode(ansChoices[4].text())}

        question = unicode(sf.questionBox.toPlainText())
        answersList = [unicode(i.text()).lower() for i in ansChoices if i.text()]
        correctAnswer = unicode(sf.correctAnswerCombo.currentText()).lower()
        st = self._currentSet()
        order = sf.questionList.row(sf.questionList.findItems(question, QtCore.Qt.MatchExactly)[0])

        # validate: at least 2 choices
        if len(answersList) < 2:
            saveError("you must enter at least 2 answer choices.")
            return

        # validate: no gaps in answer choices
        reachedEnd = False
        for i in ansChoices:
            if i.text() and reachedEnd:
                saveError("you may not leave answer choices blank unless " \
                          "they are at the end")
                return
            elif not i.text():
                reachedEnd = True

        # validate: correct answer chosen
        if correctAnswer == '':
            saveError("you must choose a correct answer")
            return

        # validate: selected answer exists
        if ansDict[correctAnswer] == '':
            saveError("you must provide an answer choice for the answer that " \
                      "you have selected as correct")
            return

        try:
            nq = Question(question, answersList, correctAnswer, st, order)
        except QuestionFormatError as qfe:
            utils.errorBox("Oops! The database returned the following " \
                    "error:\n\n %s" % qfe, "Save Error")
            return

        #TODO: indicate somehow that saving was successful?
        self.form.newButton.setFocus()

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

    ### UTILITIES ###
    def _currentSet(self):
        return db.sets.findSet(name= unicode(self.form.jumpCombo.currentText()))
