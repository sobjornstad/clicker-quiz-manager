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
import ui.utils as utils
import db.classes
import db.genquiz
import db.history

class HistoryDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self)
        self.form = Ui_Dialog()
        self.form.setupUi(self)

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
        doEnable = self.sm.hasSelection()
        sf = self.form
        for i in (sf.viewQuizButton, sf.importResultsButton,
                  sf.viewResultsButton, sf.emailResultsButton):
            i.setEnabled(doEnable)

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

    def onViewQuiz(self):
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
        d.exec_()

    def onEmailResults(self):
        pass

    def onImportResults(self):
        pass

    def onViewResults(self):
        obj = self.tableModel.getObj(self.form.tableView.currentIndex())
        zid = obj.zid
        rw = ui.results.ResultsDialog(self, self._currentClass(), zid)
        rw.exec_()

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
