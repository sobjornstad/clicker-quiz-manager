# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2015 Soren Bjornstad. All rights reserved.

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QDialog, QInputDialog, QMessageBox, QShortcut, \
     QKeySequence, QFileDialog
from PyQt4.QtCore import QObject, QAbstractTableModel, QModelIndex
from ui.forms.history import Ui_Dialog

import ui.results
import ui.quizgen
import ui.emailing
import ui.utils as utils
import db.classes
import db.genquiz
import db.history
import db.results

class HistoryDialog(QDialog):
    def __init__(self, parent, dbConf, qConf):
        QDialog.__init__(self)
        self.form = Ui_Dialog()
        self.form.setupUi(self)
        self.dbConf = dbConf
        self.qConf = qConf

        self.form.closeButton.clicked.connect(self.reject)
        self.form.viewQuizButton.clicked.connect(self.onViewQuiz)
        self.form.emailResultsButton.clicked.connect(self.onEmailResults)
        self.form.importResultsButton.clicked.connect(self.onImportResults)
        self.form.viewResultsButton.clicked.connect(self.onViewResults)

        self.setupClassCombo()
        self.tableModel = HistoryTableModel(self)
        self.form.tableView.setModel(self.tableModel)
        self.sm = self.form.tableView.selectionModel()
        self.sm.selectionChanged.connect(self.checkButtonEnablement)
        self.reFillHistory()
        self.form.classCombo.activated.connect(self.reFillHistory)

        qlShortcut = QShortcut(QKeySequence("Alt+L"), self.form.tableView)
        qlShortcut.connect(qlShortcut, QtCore.SIGNAL("activated()"), lambda: self.form.tableView.setFocus())

    def checkButtonEnablement(self):
        sf = self.form
        # if nothing is selected, disable all options and return
        if not self.sm.hasSelection():
            for i in (sf.viewQuizButton, sf.importResultsButton,
                      sf.viewResultsButton, sf.emailResultsButton):
                i.setEnabled(False)
            return

        # view quiz is always available as long as a quiz is selected
        sf.viewQuizButton.setEnabled(True)

        # import results available iff results not imported
        obj = self.tableModel.getObj(self.form.tableView.currentIndex())
        sf.importResultsButton.setEnabled(obj.resultsFlag == 0)

        # view results available if results is available or sent
        sf.viewResultsButton.setEnabled(obj.resultsFlag != 0)

        # email results available iff results is available
        # TODO: it may be better to allow emailing again, but give a warning
        sf.emailResultsButton.setEnabled(obj.resultsFlag != 0)

    def setupClassCombo(self):
        self.form.classCombo.clear()
        cl = db.classes.getAllClasses()
        for c in cl:
            self.form.classCombo.addItem(c.getName())

    def setInitialClass(self, cls):
        idx = self.form.classCombo.findText(cls.getName())
        self.form.classCombo.setCurrentIndex(idx)
        self.reFillHistory()

    def reFillHistory(self):
        cls = self._currentClass()
        history = db.history.historyForClass(cls)
        self.tableModel.replaceHistorySet(history)
        self.defaultSort()
        self.form.tableView.resizeColumnsToContents()
        self.checkButtonEnablement()

    def defaultSort(self):
        self.form.tableView.sortByColumn(0, QtCore.Qt.AscendingOrder)

    def onViewQuiz(self, isModal=True):
        obj = self.tableModel.getObj(self.form.tableView.currentIndex())
        d = ui.quizgen.PreviewDialog(self)
        d.setupForRePreview(self._currentClass(), obj.seq)
        # Fetch quiz preview and set text. self.quiz (accessed through parent
        # -- i.e., the present object) is here a QuizProvider, emulating an
        # actual Quiz
        self.quiz = db.history.QuizProvider(obj.ql, self._currentClass())
        quizPreviewText = db.output.genPlainText(
                self.quiz.fetchQuestionsForOutput())
        d.setText(quizPreviewText)
        if isModal:
            d.exec_()
        else:
            d.show()

    def onEmailResults(self):
        obj = self.tableModel.getObj(self.form.tableView.currentIndex())
        if obj.resultsFlag == 2:
            r = utils.questionBox("You have already successfully emailed the "
                    "results of this quiz to all students. Do you really want "
                    "to do it again?", " Really send email again?")
            if r != QMessageBox.Yes:
                return

        ew = ui.emailing.EmailingDialog(self, self._currentClass(),
                self._currentZid(), self.dbConf, self.qConf)
        success = ew.exec_()
        if success:
            utils.informationBox("The results were emailed successfully.",
                                 "Email complete")
            obj = self.tableModel.getObj(self.form.tableView.currentIndex())
            obj.rewriteResultsFlag(2) # results emailed

    def onImportResults(self):
        fname = QFileDialog.getOpenFileName(caption="Import Results",
                filter="HTML files (*.html)")
        if not fname:
            return
        with open(fname) as f:
            html = f.read()
        responses = db.results.parseHtmlString(html)
        for resp in responses:
            try:
                db.results.writeResults(
                        resp, self._currentClass(), self._currentZid())
            except db.results.WrongQuizError as e:
                utils.errorBox(unicode(e))
                return False
            except db.results.MissingStudentError as e:
                db.results.delResults(self._currentZid())
                extra = " The student ID numbers in the students dialog for"\
                        " this class must match the ID numbers in"\
                        " TurningPoint so that CQM can match responses with"\
                        " students. No results have been imported; please"\
                        " check and correct the list, then try importing again."
                utils.errorBox(unicode(e) + extra)
                return False

        obj = self.tableModel.getObj(self.form.tableView.currentIndex())
        obj.rewriteResultsFlag(1) # results imported, not yet sent
        self.checkButtonEnablement()
        return True

    def onViewResults(self):
        zid = self._currentZid()
        rw = ui.results.ResultsDialog(self, self._currentClass(), zid)
        needsRefresh = rw.exec_() # accept means refresh required
        if needsRefresh:
            self.reFillHistory()

    def _currentZid(self):
        obj = self.tableModel.getObj(self.form.tableView.currentIndex())
        return obj.zid

    def _currentClass(self):
        clsName = unicode(self.form.classCombo.currentText())
        cls = db.classes.getClassByName(clsName)
        return cls

class HistoryTableModel(QAbstractTableModel):
    def __init__(self, parent, l=[], *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.parent = parent
        self.l = l
        self.headerdata = ["Quiz #", "Date", "New Set(s)", "New #", "Rev #",
                           "Results"]

    def rowCount(self, parent):
        return len(self.l)
    def columnCount(self, parent):
        return len(self.headerdata)

    def data(self, index, role):
        if not index.isValid():
            return None
        if not (role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole):
            # without including EditRole, the whole cell gets wiped out when
            # an edit is begun ##TODO: do we need this in this table?
            return None

        col = index.column()
        robj = self.l[index.row()]
        if col == 0:
            return robj.seq
        elif col == 1:
            return robj.getFormattedDate()
        elif col == 2:
            return robj.newSetNames
        elif col == 3:
            return robj.newNum
        elif col == 4:
            return robj.revNum
        elif col == 5:
            return robj.getFormattedResultsFlag()

    #def setData(self, index, value, role):
    #    colNum = index.column()
    #    studentNum = index.row()
    #    robj = self.l[studentNum]
    #    value = unicode(value.toString())

    #    if colNum == 0:
    #        robj.setLn(value)
    #    elif colNum == 1:
    #        robj.setFn(value)
    #    elif colNum == 2:
    #        robj.setTpid(value)
    #    elif colNum == 3:
    #        robj.setTpdev(value)
    #    elif colNum == 4:
    #        robj.setEmail(value)

    #    self.emit(QtCore.SIGNAL("dataChanged"))
    #    return True

    def sort(self, column, order=QtCore.Qt.AscendingOrder):
        rev = not (order == QtCore.Qt.AscendingOrder)

        if column == 0:
            key = lambda i: i.seq
        elif column == 1:
            # regardless of any date format set, use YYYY-MM-DD to ensure
            # dates are sorted in correct order
            key = lambda i: i.getFormattedDate('%Y-%m-%d')
        elif column == 2:
            key = lambda i: i.newSetNames
        elif column == 3:
            key = lambda i: i.newNum
        elif column == 4:
            key = lambda i: i.revNum
        elif column == 5:
            key = lambda i: i.getFormattedResultsFlag()

        self.beginResetModel()
        self.l.sort(key=key, reverse=rev)
        self.endResetModel()

    def flags(self, index):
        q = QtCore.Qt
        return q.ItemIsSelectable | q.ItemIsEnabled# | q.ItemIsEditable

    def headerData(self, col, orientation, role):
        if (orientation == QtCore.Qt.Horizontal and
                role == QtCore.Qt.DisplayRole):
            return self.headerdata[col]
        else:
            return None

    def replaceHistorySet(self, newList):
        self.l = newList
        self.reset()

    def numItems(self):
        return len(self.l)

    def getObj(self, index):
        return self.l[index.row()]
