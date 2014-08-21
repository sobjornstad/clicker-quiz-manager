# -*- encoding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QDialog, QMessageBox, QInputDialog, QPlainTextEdit, \
     QComboBox, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from forms.editset import Ui_Dialog

import utils
from db.sets import getAllSets
from db.questions import Question, QuestionFormatError, DuplicateError
import db.sets, db.questions

class AutosaveQPlainTextEdit(QPlainTextEdit):
    def focusOutEvent(self, event):
        super(AutosaveQPlainTextEdit, self).focusOutEvent(event)
        self.window().onQuestionFocusOut()

class SetEditor(QDialog):
    def __init__(self, setList):
        QDialog.__init__(self)
        self.sl = setList
        self.form = Ui_Dialog()
        self.form.setupUi(self)

        sf = self.form
        self.ansChoices = [sf.answerA, sf.answerB, sf.answerC, sf.answerD,
                sf.answerE]

        # get buttons into proper state of enablement
        self.listEnabled = True
        self._disableList()
        self._enableList()

        self.populateSets()
        self.qm = db.questions.QuestionManager(self._currentSet())
        self.populateQuestions()
        # select first question, or create new one if there are none
        if self.form.questionList.count():
            self.form.questionList.setCurrentRow(0)
            self.onQuestionChange()
            self.form.questionList.setFocus()
        else:
            self.onNew()
            # we don't want to be able to cancel the only question that exists
            self.form.cancelButton.setEnabled(False)

        self.form.correctAnswerCombo.activated.connect(self.onCorrectAnswerChoice)
        self.form.jumpCombo.activated.connect(self.onJumpToSet)
        self.form.questionList.itemSelectionChanged.connect(self.onQuestionChange)

        self.form.newButton.clicked.connect(self.onNew)
        self.form.deleteButton.clicked.connect(self.onDelete)
        self.form.importButton.clicked.connect(self.onImport)
        self.form.exportButton.clicked.connect(self.onExport)
        self.form.moveDownButton.clicked.connect(self.onMoveDown)
        self.form.moveUpButton.clicked.connect(self.onMoveUp)
        self.form.saveButton.clicked.connect(self.onSaveQuestion)
        self.form.cancelButton.clicked.connect(self.onDiscard)
        self.form.closeButton.clicked.connect(self.reject)

        self.form.questionBox.textChanged.connect(self.updateListQuestion)
        self.form.answerA.textEdited.connect(self._disableList)
        self.form.answerB.textEdited.connect(self._disableList)
        self.form.answerC.textEdited.connect(self._disableList)
        self.form.answerD.textEdited.connect(self._disableList)
        self.form.answerE.textEdited.connect(self._disableList)
        self.form.difficultySpinner.valueChanged.connect(self._disableList)
        self.form.correctAnswerCombo.activated.connect(self._disableList)

    def reject(self):
        if self.listEnabled:
            super(SetEditor, self).reject()
        else:
            d = QDialog(self)

            txt = QLabel("Do you want to save your changes to the current question?")
            txtBox = QHBoxLayout()
            txtBox.addWidget(txt)

            a = QPushButton("Save")
            a.clicked.connect(self.onExitSave)
            b = QPushButton("Don't Save")
            b.clicked.connect(self.onExitDiscard)
            c = QPushButton("Cancel")
            c.clicked.connect(d.close)
            bBox = QHBoxLayout()
            bBox.addWidget(a)
            bBox.addWidget(b)
            bBox.addWidget(c)

            vBox = QVBoxLayout()
            vBox.addLayout(txtBox)
            vBox.addLayout(bBox)
            d.setLayout(vBox)
            d.show()
            self.rejectDialog = d
    def onExitSave(self):
        if self._saveQuestion():
            super(SetEditor, self).reject()
        else:
            self.rejectDialog.close()
    def onExitDiscard(self):
        super(SetEditor, self).reject()

    def populateSets(self):
        self.l = getAllSets()
        for s in self.l:
            self.form.jumpCombo.addItem(s.getName())

        # select the set we're editing from it
        set = self.sl.form.setList.currentItem().text()
        i = self.form.jumpCombo.findText(set)
        self.form.jumpCombo.setCurrentIndex(i)

    def populateQuestions(self):
        """Fill list box with existing questions in the set."""

        for i in self.qm:
            self.form.questionList.addItem(i.getQuestion())

    def populateCorrectAnswer(self, isNewQuestion):
        """
        Clear any current contents of the correct answer box and add options
        A-E. It would be ideal to only fill the ones that the user had
        selected, but we appear to have run into Qt bugs there:
        http://goo.gl/mQ1b83.

        If isNewQuestion, a blank option will be added to the top of the list,
        to be removed once an option is selected.
        """

        self.form.correctAnswerCombo.clear()
        if isNewQuestion:
            self.form.correctAnswerCombo.addItem("", 0) # no choice selected yet
        for ans in ['A', 'B', 'C', 'D', 'E']:
            self.form.correctAnswerCombo.addItem(ans, 0)

    def onCorrectAnswerChoice(self):
        """Remove the blank item from the list once the combo box is activated
        for the first time. See the docstring for populateCorrectAnswer()."""

        i = self.form.correctAnswerCombo.findText("")
        self.form.correctAnswerCombo.removeItem(i)

    def onQuestionChange(self):
        q = self.qm.byName(
            unicode(self.form.questionList.currentItem().text()))
        if not q:
            # the question isn't in the db yet, so it's an empty question
            # and will be handled by onNew
            return
        #TODO: consider if maybe this should store the Question object in future
        self.currentQid = q.getQid()
        self.form.questionBox.setPlainText(q.getQuestion())

        self._clearQuestionInterface()
        a = q.getAnswersList()
        for i in range(len(a)):
            self.ansChoices[i].setText(a[i])

        i = Question._qLetters.index(q.getCorrectAnswer())
        self.populateCorrectAnswer(False)
        self.form.correctAnswerCombo.setCurrentIndex(i)

    def _clearQuestionInterface(self):
        """Remove answers, difficult, and correct answer from question side.
        Don't touch question, as we'll need to set that to the new or existing
        question value anyway."""

        self.form.difficultySpinner.setValue(1)
        for i in self.ansChoices:
            i.setText("")
        self.populateCorrectAnswer(True)

    def _findNqText(self):
        """Determine what text to use for the "new question" boilerplate."""

        ql = self.form.questionList
        qtexts = [unicode(ql.item(i).text()) for i in range(ql.count())]
        nq = "New Question"
        return self._makeNameUnique(nq, qtexts)

    def onNew(self):
        self.currentQid = None
        self._clearQuestionInterface()
        self._disableList()
        nqText = self._findNqText()
        self.form.questionList.addItem(nqText)
        newRow = self.form.questionList.count() - 1
        self.form.questionList.setCurrentRow(newRow)
        self.form.questionBox.setPlainText(nqText)
        self.form.questionBox.setFocus()
        self.form.questionBox.selectAll()

    def onDiscard(self):
        self._enableList()
        if self.currentQid:
            # editing; restore to state of db
            self.onQuestionChange()
        else:
            # new; delete entry entirely
            cRow = self.form.questionList.currentRow()
            self.form.questionList.takeItem(cRow)

    def updateListQuestion(self):
        """Called when user edits the question, to keep the question's entry in the
        list in sync."""

        txt = unicode(self.form.questionBox.toPlainText())
        self.form.questionList.currentItem().setData(0, txt)
        if self.currentQid and self.qm.byId(self.currentQid).getQuestion() != txt:
            # user has edited the text of a question that is in the db, as
            # opposed to just the program changing the contents of the question
            # side or a new question
            self._disableList()

    def onQuestionFocusOut(self):
        pass

    def onSaveQuestion(self):
        "Called when clicking the 'save changes' button."

        self._saveQuestion()

        #TODO: indicate somehow that saving was successful?
        self.form.newButton.setFocus()

    def _saveQuestion(self):
        """Save the current question to the database. Return True if
        successful, False if an error, and display the appropriate error."""

        def saveError(msg):
            deferror = "The question you provided is invalid: %s." % msg
            utils.errorBox(deferror, "Save Error")

        sf = self.form
        ansDict = {'a': unicode(self.ansChoices[0].text()),
                   'b': unicode(self.ansChoices[1].text()),
                   'c': unicode(self.ansChoices[2].text()),
                   'd': unicode(self.ansChoices[3].text()),
                   'e': unicode(self.ansChoices[4].text())}

        question = unicode(sf.questionBox.toPlainText())
        answersList = [unicode(i.text()) for i in self.ansChoices if i.text()]
        correctAnswer = unicode(sf.correctAnswerCombo.currentText()).lower()
        st = self._currentSet()
        order = sf.questionList.row(sf.questionList.findItems(question, QtCore.Qt.MatchExactly)[0])

        # validate: at least 2 choices
        if len(answersList) < 2:
            saveError("you must enter at least 2 answer choices")
            return False

        # validate: no gaps in answer choices
        reachedEnd = False
        for i in self.ansChoices:
            if i.text() and reachedEnd:
                saveError("you may not leave answer choices blank unless " \
                          "they are at the end")
                return False
            elif not i.text():
                reachedEnd = True

        # validate: correct answer chosen
        if correctAnswer == '':
            saveError("you must choose a correct answer")
            return False

        # validate: selected answer exists
        if ansDict[correctAnswer] == '':
            saveError("you must provide an answer choice for the answer that " \
                      "you have selected as correct")
            return False

        if self.currentQid is not None:
            # update the existing one
            nq = self.qm.byId(self.currentQid)
            nq.setQuestion(question)
            nq.setAnswersList(answersList)
            nq.setCorrectAnswer(correctAnswer)
            # order and set can't have changed from this operation
        else:
            try:
                nq = Question(question, answersList, correctAnswer, st, order)
            except QuestionFormatError as qfe:
                # this shouldn't happen unless we screwed up
                utils.errorBox("Oops! The database returned the following " \
                        "error:\n\n %s" % qfe, "Save Error")
                return False

        self.qm.update()
        self._enableList()
        return True

    def onDelete(self):
        r = utils.confirmDeleteBox("question", "")
        if r != QMessageBox.Yes:
           return
        cRow = self.form.questionList.currentRow()
        q = self.qm.byOrd(cRow)
        self.qm.rmQuestion(q)
        self.form.questionList.takeItem(cRow)

    def onImport(self):
        utils.informationBox("This feature is not implemented yet.", "Sorry!")

    def onExport(self):
        utils.informationBox("This feature is not implemented yet.", "Sorry!")

    def onMoveDown(self):
        self._move('down')
    def onMoveUp(self):
        self._move('up')

    def onJumpToSet(self):
        utils.informationBox("This feature is not implemented yet.", "Sorry!")


    ### UTILITIES ###
    def _currentSet(self):
        return db.sets.findSet(name= unicode(self.form.jumpCombo.currentText()))

    def _move(self, direction):
        #TODO: This is essentially identical to the one in the sets code. We
        # might be able to get some mileage out of a superclass.
        assert direction in ('up', 'down'), "Invalid direction passed to _move"

        cRow = self.form.questionList.currentRow()
        maxRow = self.form.questionList.count() - 1
        if (cRow == 0 and direction == 'up') or (
                cRow == maxRow and direction == 'down'):
            # assume the user will know what she did wrong; keep our mouth shut
            return

        q1 = self.qm.byOrd(cRow)
        q2 = self.qm.byOrd(cRow-1 if direction == 'up' else cRow+1)
        db.questions.swapRows(q1, q2)
        self.qm.update()

        ql = self.form.questionList
        i = ql.takeItem(cRow)
        ql.insertItem(cRow-1 if direction == 'up' else cRow+1, i)
        ql.setCurrentRow(cRow-1 if direction == 'up' else cRow+1)

    def _makeNameUnique(self, name, compare):
        """
        Append a number as necessary to make some name unique in a list.

        Arguments: name to make unique, list of strings to compare to for
        uniqueness.
        """
        nn = name
        if name in compare:
            nn = name + " 2"
            while nn in compare:
                num = int(nn.split(' ')[-1])
                nn = name + str(num+1)
        return nn

    def _disableList(self):
        if self.listEnabled:
            self._changeListStatus('disabled')
    def _enableList(self):
        if not self.listEnabled:
            self._changeListStatus('enabled')
    def _changeListStatus(self, which):
        sf = self.form
        elements = [
                    sf.questionList, sf.newButton,
                    sf.deleteButton, sf.importButton,
                    sf.moveUpButton, sf.moveDownButton,
                    sf.exportButton, sf.jumpCombo,
                   ]
        reverseElements = [sf.cancelButton, sf.saveButton]

        if which == 'enabled':
            self.listEnabled = True
            for i in elements:
                i.setEnabled(True)
            for i in reverseElements:
                i.setEnabled(False)
        elif which == 'disabled':
            self.listEnabled = False
            for i in elements:
                i.setEnabled(False)
            for i in reverseElements:
                i.setEnabled(True)
        else:
            assert False, "Invalid argument to _changeListStatus!"
