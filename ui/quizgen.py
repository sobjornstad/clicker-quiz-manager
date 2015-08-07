# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2014 Soren Bjornstad. All rights reserved.

from time import sleep

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QDialog, QMessageBox, QFileDialog, QApplication, QCursor
from PyQt4.QtCore import QObject
from forms.quizgen import Ui_Dialog
import forms.qprev

import db.classes
import db.genquiz
import db.sets
import db.questions
import ui.utils as utils
from db.output import LatexError

class QuizWindow(QDialog):
    def __init__(self, mw, selectedNewSet=None):
        # mw is not always mw: it can also be the question dialog! I have not
        # copied it into self to ensure that we notice this if we want to use
        # some mw method/attribute in the future.
        QDialog.__init__(self)
        self.autoselectSet = selectedNewSet
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
        self.updateDueValues(0, 0)
        self.populateClasses()

    def populateSets(self):
        self.form.setList.clear()
        self.sets = db.genquiz.findNewSets(self.cls)
        for s in self.sets:
            self.form.setList.addItem(s.getName())
        # if there is a set we're trying to automatically select and it exists
        # in the current class's list, select it
        if self.autoselectSet:
            s = self.form.setList.findItems(self.autoselectSet.getName(),
                    QtCore.Qt.MatchExactly)
            if s:
                self.form.setList.setCurrentItem(s[0])
                self.onSetChange()

    def populateClasses(self):
        self.classes = db.classes.getAllClasses()
        for c in self.classes:
            self.form.classCombo.addItem(c.getName())
        self.onClassChange()

    def updateDueValues(self, news, revs):
        self.form.newDisplay.setText("(%i available)" % (news))
        self.form.reviewDisplay.setText("(%i available)" % (revs))

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
            topText = "This quiz contains %i new question%s and %i review%s.\n"
            topText += "New questions are from %s %s."
            sns, n = sq.getSetNames()
            topText = topText % (sq.useNewNum, 's' if sq.useNewNum != 1 else '',
                                 sq.useRevNum, 's' if sq.useRevNum != 1 else '',
                                 'the following sets:' if n != 1 else 'the set',
                                 sns)

        prevText = '\n\n'.join([topText, prevText])
        d = PreviewDialog(self)
        d.setText(prevText)
        d.exec_()

        #### maybe make this a return val later? not sure
        if self.previewResult:
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

    ftdict = {
              'rtf': 'Rich text files (*.rtf)',
              'pdf': 'PDF files (*.pdf)',
              'html': 'HTML files (*.html)',
              'txt': 'Text files (*)',
             }

    def __init__(self, parent=None):
        QDialog.__init__(self)
        self.parent = parent
        self.form = forms.qprev.Ui_Dialog()
        self.form.setupUi(self)

        self.form.formatCombo.addItem("TurningPoint Quiz (*.rtf)")
        self.form.formatCombo.addItem("Paper Quiz (*.pdf)")
        self.form.formatCombo.addItem("HTML (with answers & set names)")
        self.form.formatCombo.addItem("HTML (no answers or set names)")
        self.form.formatCombo.addItem("Plain Text (with answers & set names)")
        self.form.formatCombo.addItem("Plain Text (no answers or set names)")

        self.form.okButton.clicked.connect(self.accept)
        self.form.cancelButton.clicked.connect(self.reject)
        self.form.saveButton.clicked.connect(self.onSave)
        self.hasSaved = False

    def setSaved(self):
        self.hasSaved = True
        self.form.okButton.setEnabled(True)

    def setText(self, txt):
        self.form.prevText.setPlainText(txt)
        if "quiz is blank" in txt:
            self.form.okButton.setEnabled(False)
            self.form.saveButton.setEnabled(False)
            self.form.formatCombo.setEnabled(False)

    def onSave(self):
        selection = self.form.formatCombo.currentText()
        try:
            questions = self.parent.quiz.fetchQuestionsForOutput()
            if 'rtf' in selection:
                fname = self.getFilename('rtf')
                if fname:
                    db.output.renderRTF(questions, fname)
                else:
                    return
            elif 'pdf' in selection:
                fname = self.getFilename('pdf')
                cls = self.parent.quiz.getClass()
                quizNum = db.genquiz.getSetsUsed(cls) + 1
                if fname:
                    QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))
                    try:
                        db.output.renderPdf(questions, cls, quizNum, doOpen=False,
                                doCopy=True, copyTo=fname)
                    except LatexError as err:
                        QApplication.restoreOverrideCursor()
                        txt = """
An error occurred while running LaTeX to create the paper quiz. Please check the error and contact the developer if you are unsure how to correct it. The error text is as follows:

%s
""".strip()
                        txt = txt % str(err)
                        ebw = utils.ErrorBoxWindow()
                        ebw.setErrorText(txt, includeErrorBoilerplate=False)
                        ebw.exec_()
                    else:
                        QApplication.restoreOverrideCursor()
                else:
                    return
            elif 'HTML' in selection:
                fq = ('no' in selection)
                fname = self.getFilename('html')
                cls = self.parent.quiz.getClass()
                quizNum = db.genquiz.getSetsUsed(cls) + 1
                if fname:
                    db.output.renderHtml(questions, cls, quizNum, fname, fq)
                else:
                    return
            elif 'Plain Text' in selection:
                fq = ('no' in selection)
                fname = self.getFilename('txt')
                cls = self.parent.quiz.getClass()
                quizNum = db.genquiz.getSetsUsed(cls) + 1
                if fname:
                    db.output.renderTxt(questions, cls, quizNum, fname, fq)
                else:
                    return
        except:
            raise
        else:
            self.setSaved()

    def getFilename(self, filetype):
        ft = PreviewDialog.ftdict[filetype]
        f = QFileDialog.getSaveFileName(caption="Export Quiz", filter=ft)
        if not f:
            return None
        else:
            # on linux, the extension might not be automatically appended
            f = unicode(f)
            if filetype == 'rtf' and not f.endswith('.rtf'):
                f += '.rtf'
            elif filetype == 'pdf' and not f.endswith('.pdf'):
                f += '.pdf'
            elif filetype == 'html' and not f.endswith('.html'):
                f += '.html'
            return f

    def accept(self):
        r = utils.questionBox("Rescheduling will place your selected new sets "
                              "into review and schedule any review sets "
                              "further into the future. Rescheduling cannot "
                              "be undone. Continue?", "Confirm Reschedule")
        if r == QMessageBox.Yes:
            self.parent.quiz.rewriteSchedule()
            self.parent.previewResult = True
            utils.informationBox("The quiz was exported successfully. "
                                 "Sets have been rescheduled.",
                                 "Quiz generated")
            QDialog.accept(self)

    def reject(self):
        if self.hasSaved:
            r = utils.questionBox("If you return to the settings now, no "
                   "history entry will be saved for this quiz and the selected "
                   "new set(s) will not be scheduled for review. You should "
                   "continue only if you do not want to use this quiz in your "
                   "class. Really continue?", "Really cancel reschedule?")
            if r != QMessageBox.Yes:
                return
        self.parent.previewResult = False
        QDialog.reject(self)
