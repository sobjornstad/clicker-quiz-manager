# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2014 Soren Bjornstad. All rights reserved.

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QDialog, QMessageBox, QInputDialog, QPlainTextEdit, \
     QComboBox, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QShortcut,   \
     QKeySequence, QSpinBox, QFileDialog
from forms.editset import Ui_Dialog

import utils
from db.sets import getAllSets
from db.questions import Question, QuestionFormatError, DuplicateError
import db.sets, db.questions

class SetEditor(QDialog):
    def __init__(self, setList, config):
        QDialog.__init__(self)
        self.sl = setList
        self.config = config
        self.form = Ui_Dialog()
        self.form.setupUi(self)

        sf = self.form
        self.ansChoices = [sf.answerA, sf.answerB, sf.answerC, sf.answerD,
                sf.answerE]

        # get buttons into proper state of enablement
        self.listEnabled = True
        self._disableList()
        self._enableList()

        # fill with content
        self.populateSets()
        self.setupQuestions()

        # connect buttons
        self.form.newButton.clicked.connect(self.onNew)
        self.form.deleteButton.clicked.connect(self.onDelete)
        self.form.importButton.clicked.connect(self.onImport)
        self.form.exportButton.clicked.connect(self.onExport)
        self.form.genQuizButton.clicked.connect(self.onGenerate)
        self.form.randomizeButton.clicked.connect(self.onRandomize)
        self.form.moveDownButton.clicked.connect(self.onMoveDown)
        self.form.moveUpButton.clicked.connect(self.onMoveUp)
        self.form.saveButton.clicked.connect(self.onSaveQuestion)
        self.form.cancelButton.clicked.connect(self.onDiscard)
        self.form.closeButton.clicked.connect(self.reject)

        # connect changed events and shortcuts
        self.form.correctAnswerCombo.activated.connect(self.onCorrectAnswerChoice)
        self.form.jumpCombo.activated.connect(self.onJumpToSet)
        self.form.questionList.itemSelectionChanged.connect(self.onQuestionChange)
        qlShortcut = QShortcut(QKeySequence("Alt+L"), self.form.questionList)
        qlShortcut.connect(qlShortcut, QtCore.SIGNAL("activated()"), self.form.questionList.setFocus)
        saveShortcut = QShortcut(QKeySequence("Ctrl+S"), self.form.saveButton)
        saveShortcut.connect(saveShortcut, QtCore.SIGNAL("activated()"), self.onSaveQuestion)
        self.form.questionList.model().rowsMoved.connect(self.onDragDrop)

        self.form.questionBox.textChanged.connect(self.updateListQuestion)
        self.form.answerA.textEdited.connect(self._disableList)
        self.form.answerB.textEdited.connect(self._disableList)
        self.form.answerC.textEdited.connect(self._disableList)
        self.form.answerD.textEdited.connect(self._disableList)
        self.form.answerE.textEdited.connect(self._disableList)
        self.form.correctAnswerCombo.activated.connect(self._disableList)

    def setupQuestions(self):
        self.qm = db.questions.QuestionManager(self._currentSet())
        self.populateQuestions()
        self._updateQuestionTotal()
        # select first question, or create new one if there are none
        if self.form.questionList.count():
            self.form.questionList.setCurrentRow(0)
            self.onQuestionChange()
            self.form.questionList.setFocus()
        else:
            self.forceNewQuestion()

    def forceNewQuestion(self):
        """Used to set up the question editor when there are no existing
        questions and we need to make one before we can do anything else."""

        self.onNew()
        # we don't want to be able to cancel the only question that exists
        self.form.cancelButton.setEnabled(False)

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

        If isNewQuestion and configuration option /autoAnsA/ not set, a blank
        option will be added to the top of the list, to be removed once an
        option is selected.
        """

        self.form.correctAnswerCombo.clear()
        if isNewQuestion and not self.sl.mw.autoAnsA:
            self.form.correctAnswerCombo.addItem("", 0) # no choice selected yet
        for ans in [i.upper() for i in Question.qLetters]:
            self.form.correctAnswerCombo.addItem(ans, 0)

    def reject(self):
        if not self._ensureNotMostA():
            self.tooManyAsMessage()

        if self.listEnabled:
            super(SetEditor, self).reject()
        else:
            d = QDialog(self)

            txt = QLabel("Do you want to save your changes to the current question?")
            txtBox = QHBoxLayout()
            txtBox.addWidget(txt)

            a = QPushButton("&Save")
            a.clicked.connect(self.onExitSave)
            b = QPushButton("&Don't Save")
            b.clicked.connect(self.onExitDiscard)
            c = QPushButton("&Cancel")
            c.clicked.connect(d.close)
            bBox = QHBoxLayout()
            bBox.addWidget(a)
            bBox.addWidget(b)
            bBox.addWidget(c)

            vBox = QVBoxLayout()
            vBox.addLayout(txtBox)
            vBox.addLayout(bBox)
            d.setLayout(vBox)
            d.setWindowTitle("Save question?")
            d.show()
            self.rejectDialog = d
    def onExitSave(self):
        self.rejectDialog.close()
        if self._saveQuestion():
            super(SetEditor, self).reject()
    def onExitDiscard(self):
        self.rejectDialog.close()
        super(SetEditor, self).reject()

    def onCorrectAnswerChoice(self):
        """Remove the blank item from the list once the combo box is activated
        for the first time. See the docstring for populateCorrectAnswer()."""

        i = self.form.correctAnswerCombo.findText("")
        self.form.correctAnswerCombo.removeItem(i)

    def onQuestionChange(self):
        """
        Updates the question side of the dialog when:
        - a different item is selected from the question list
        - changes are discarded

        Also resets self.currentQid to the id of the new question.
        """

        try:
            q = self.qm.byName(
                unicode(self.form.questionList.currentItem().text()))
        except AttributeError:
            # no questions are left; this is handled in onDelete
            return

        if not q:
            if not self.currentQid:
                # the question isn't in the db yet, so it's an empty question
                # and will be handled by onNew
                return
            else:
                # the question has been modified and we're wanting to restore
                # it; change to the old db entry
                q = self.qm.byId(self.currentQid)

        #TODO: consider if maybe this should store the Question object in future
        self.currentQid = q.getQid()
        self.form.questionBox.setPlainText(q.getQuestion())

        self._clearQuestionInterface()
        a = q.getAnswersList()
        for i in range(len(a)):
            self.ansChoices[i].setText(a[i])

        i = Question.qLetters.index(q.getCorrectAnswer())
        self.populateCorrectAnswer(False)
        self.form.correctAnswerCombo.setCurrentIndex(i)

    def _clearQuestionInterface(self):
        """Remove answers, difficult, and correct answer from question side.
        Don't touch question, as we'll need to set that to the new or existing
        question value anyway."""

        for i in self.ansChoices:
            i.setText("")
        self.populateCorrectAnswer(True)

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

    def _findNqText(self):
        """Determine what text to use for the "new question" boilerplate."""

        ql = self.form.questionList
        qtexts = [unicode(ql.item(i).text()) for i in range(ql.count())]
        nq = "New Question"
        return self._makeNameUnique(nq, qtexts)

    def onDiscard(self):
        if self.currentQid:
            # We were editing; restore to state of db.

            # self.onQuestionChange() will screw up if we have happened to edit
            # the question to the exact name of an existing question, so we
            # need to temporarily change the name to something else if this is
            # the case.
            qtexts = [self.form.questionList.item(i).text()
                    for i in range(self.form.questionList.count())]
            if qtexts.count(unicode(self.form.questionBox.toPlainText())) != 1:
                temporaryName = self._makeNameUnique("del", qtexts)
                self.form.questionBox.setPlainText(temporaryName)
            self.onQuestionChange()
        else:
            # new; delete entry entirely
            cRow = self.form.questionList.currentRow()
            self.form.questionList.takeItem(cRow)
        self._enableList()

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

    def onSaveQuestion(self):
        "Called when clicking the 'save changes' button."

        r = self._saveQuestion()
        if r == 1: # edited; go back to qlist
            self.form.questionList.setFocus()
        elif r == 2: # new; expect to create another new
            self.form.newButton.setFocus()

    def _saveQuestion(self):
        """
        Save the current question to the database, displaying an appropriate
        error if necessary.
        
        Return:
        - 2 if a new question was created.
        - 1 if an old question was updated.
        - 0 if nothing was changed due to an error.
        """

        def saveError(msg):
            utils.errorBox(msg, "Invalid question")
        def handleError(err):
            """
            Rewrite error messages returned by the db layer to the more
            specific context here, as appropriate. Not all errors are checked
            for, as some of them can only come up in this context due to a
            programming error.

            Returns true if error handled, False if we passed the db's error
            on to the user.
            """

            msg = ''
            err = str(err)
            if "must have 2-5 answers" in err:
                msg = "You must enter at least two answer choices."
            elif "may not be blank" in err:
                msg = "You may not leave answer choices blank unless they " \
                      "are at the end."
            elif "correct answer must be specified" in err:
                msg = "You must choose a correct answer."
            elif "specified must be an answer choice" in err:
                msg = "The answer you have selected as correct does not have " \
                      "any text."
            elif "The question must have some text" in err:
                msg = "Please enter some text in the question field."
            elif "different choices cannot have the same text" in err:
                msg = "You may not use the same text for two different " \
                      "answers."

            if msg:
                utils.errorBox(msg, "Invalid question")
                return True
            else:
                # this shouldn't happen unless we screwed up
                utils.errorBox("Oops! The database returned the following " \
                        "error:\n\n%s" % qfe, "Save Error")
                return False


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

         # Make sure there are no gaps in answer choices; this can't be
         # detected on the db side because we skip over all blanks when filling
         # the answer list.
        reachedEnd = False
        for i in self.ansChoices:
            if i.text() and reachedEnd:
                saveError("You may not leave answer choices blank unless " \
                          "they are at the end.")
                return False
            elif not i.text():
                reachedEnd = True

        try:
            if self.currentQid is not None:
                # update the existing question

                nq = self.qm.byId(self.currentQid)
                nq.prevalidate()
                # strip whitespace from question. If we don't update the text
                # box as well, the dialog goes haywire if it gets changed and
                # we try to look at a different question.
                question = question.strip()
                self.form.questionBox.setPlainText(question)

                nq.setQuestion(question)
                nq.setAnswersList(answersList)
                nq.setCorrectAnswer(correctAnswer)
                retVal = 1
                # order and set can't have changed from this operation
            else:
                # create a new one
                nq = Question(question, answersList, correctAnswer, st, order)
                retVal = 2
        except DuplicateError:
            saveError("You already have a question with that text.")
            return False
        except QuestionFormatError as qfe:
            handleError(qfe)
            return False

        self.qm.update()
        self.currentQid = self.qm.byName(question).getQid()
        self._updateQuestionTotal()
        self._enableList()
        return retVal

    def _updateQuestionTotal(self):
        numQs = self.form.questionList.count()
        self.form.questionTotalDisplay.setText("Questions: %i" % numQs)

    def onDelete(self):
        r = utils.confirmDeleteBox("question", "")
        if r != QMessageBox.Yes:
           return
        cRow = self.form.questionList.currentRow()
        q = self.qm.byOrd(cRow)
        self.qm.rmQuestion(q)
        self.form.questionList.takeItem(cRow)
        self._updateQuestionTotal()
        if not self.form.questionList.count():
            self.forceNewQuestion()

    def onImport(self):
        import db.qimport
        f = QFileDialog.getOpenFileName(caption="Import File",
                filter="Text files (*.txt);;All files (*)")
        if not f:
            return
        importer = db.qimport.Importer(f, self._currentSet())
        errors = importer.txtImport()

        self.form.questionList.clear()
        self.setupQuestions()

        if errors:
            utils.tracebackBox("Import returned the following errors:\n%s\n\nAny " \
                               "lines that were valid have been imported." \
                               % errors, "Import Results", False)
        else:
            utils.informationBox("Import completed successfully.",
                    "Import Results")

    def onExport(self):
        utils.informationBox("This feature is not implemented yet.", "Sorry!")

    def onGenerate(self):
        if not utils.ensureClassExists():
            utils.errorBox("Please create a class from the main window before" \
                    " generating a quiz.", "No Classes")
            return

        if not self._ensureNotMostA():
            self.tooManyAsMessage()

        import quizgen
        qsw = quizgen.QuizWindow(self, self.config, self._currentSet())
        qsw.exec_()

    def onRandomize(self):
        for q in self.qm:
            q.randomizeChoices()
        self.qm.update()
        self._reloadQuestions()

    def onDragDrop(self, start, end, parent, destination, row):
        """
        Start, parent, and destination appear to only be important when dealing
        with complex nested lists or with moving multiple things at once. As it
        is, end gives the start row index and row the final row index.
        """

        mFrom = end
        mTo = row
        db.questions.insertQuestion(self.qm.byOrd(mFrom), mTo)
        self.qm.update()

    def onMoveDown(self):
        self._move('down')
    def onMoveUp(self):
        self._move('up')
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

    def onJumpToSet(self):
        self._reloadQuestions()
        # user might want to move down several with the arrow keys
        self.form.jumpCombo.setFocus()


    ### UTILITIES ###
    def _reloadQuestions(self):
        self.form.questionList.clear()
        self.setupQuestions()

    def _currentSet(self):
        return db.sets.findSet(name= unicode(self.form.jumpCombo.currentText()))

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
                    sf.randomizeButton, sf.genQuizButton,
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

    def _ensureNotMostA(self):
        """
        If there are an unusual number of 'A' choices for questions in the
        current set, perhaps the user forgot to randomize the questions and
        should be warned.
        """

        ATally = 0
        totalQs = self.form.questionList.count()
        for q in db.questions.getBySet(self._currentSet()):
            if q.getCorrectAnswer() == 'a':
                ATally += 1

        ratio = float(ATally) / totalQs
        if (ratio >= 0.5 and totalQs > 5) or (ratio >= 0.75 and totalQs > 1):
            return False
        else:
            return True

    def tooManyAsMessage(self):
        utils.warningBox("An unusual percentage of your correct " \
                "answers are A. Maybe you forgot to randomize the answers?",
                "Heads up!")
