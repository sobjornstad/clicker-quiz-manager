# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2015 Soren Bjornstad. All rights reserved.

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QDialog, QInputDialog, QMessageBox, QShortcut, \
     QKeySequence, QFileDialog
from PyQt4.QtCore import QObject, QAbstractTableModel, QModelIndex
from ui.forms.results import Ui_Dialog

import ui.utils as utils
import db.results
import db.classes
import db.students
from db.history import HistoryItem

class ResultsDialog(QDialog):
    """
    A dialog displaying the results of a given quiz in a given class.
    """

    def __init__(self, parent, cls, zid):
        """
        Arguments:
            parent: parent widget
            cls: the Class this quiz belongs to
            zid: the Quiz to display results for
        """
        QDialog.__init__(self)
        self.form = Ui_Dialog()
        self.form.setupUi(self)
        self.parent = parent
        self.cls = cls
        self.zid = zid

        self.form.closeButton.clicked.connect(self.reject)
        self.form.viewQuizButton.clicked.connect(self.onViewQuiz)
        self.form.deleteResultsButton.clicked.connect(self.onDeleteResults)

        self.tableModel = AnswersTableModel(self)
        self.form.stuAnswersTable.setModel(self.tableModel)
        self.form.studentsTable.itemSelectionChanged.connect(
                self.displayStudent)

        qlShortcut = QShortcut(QKeySequence("Alt+L"), self.form.studentsTable)
        qlShortcut.connect(qlShortcut, QtCore.SIGNAL("activated()"),
                self.form.studentsTable.setFocus)

        # initialize lists
        self.setupStudentList()
        self.setupSummaryData()
        self.form.studentsTable.setCurrentRow(0)
        self.displayStudent()

    def setupSummaryData(self):
        self.form.classLabel.setText(self.cls.getName())
        historyItem = HistoryItem(self.zid)
        self.form.quizLabel.setText(unicode(historyItem.seq))
        self.form.newSetsLabel.setText(unicode(historyItem.newSetNames))

        avgCorrect, totalNum, avgPercentage = db.results.calcClassAverages(
                self.students, self.zid)
        self.form.averageLabel.setText("%.02f/%i (%.01f%%)" % (
            avgCorrect, totalNum, 100 * avgCorrect / totalNum))
        self.setWindowTitle("%s ~ Results for Quiz %i" % (
            self.cls.getName(), historyItem.seq))

    def setupStudentList(self):
        self.students = db.students.studentsInClass(self.cls)
        # sort by last name, then first name
        self.students.sort(key=lambda i: i.getFn())
        self.students.sort(key=lambda i: i.getLn())
        for stu in self.students:
            self.form.studentsTable.addItem("%s, %s"%(stu.getLn(), stu.getFn()))

    def displayStudent(self):
        studentIndex = self.form.studentsTable.currentRow()
        selectedStudent = self.students[studentIndex]
        self.form.stuNameLabel.setText("%s, %s" % (
            selectedStudent.getLn(), selectedStudent.getFn()))

        results = db.results.readResults(selectedStudent, self.zid)
        if results is not None:
            self.tableModel.replaceContents(results)
            numCorrect, numTotal, percent = db.results.calcCorrectValues(results)
            scoreStr = "%i/%i (%.01f%%)" % (numCorrect, numTotal, percent)
            self.form.stuScoreLabel.setText(scoreStr)
        else:
            self.tableModel.replaceContents([])
            self.form.stuScoreLabel.setText("(no results)")

    def onViewQuiz(self):
        self.parent.onViewQuiz()

    def onDeleteResults(self):
        r = utils.questionBox("Are you sure you want to delete these results? "
                             "You will no longer be able to view them, but if "
                             "you still have the TurningPoint statistics, you "
                             "can import them again.")
        if not r:
            return
        db.results.delResults(self.zid)
        historyItem = HistoryItem(self.zid)
        historyItem.rewriteResultsFlag(0)
        self.accept() # interpreted by caller as needing a table refresh


class AnswersTableModel(QAbstractTableModel):
    def __init__(self, parent, l=[], *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.parent = parent
        self.l = l
        self.headerdata = ["#", "Answer", "Correct"]

    def rowCount(self, parent):
        return len(self.l) if self.l is not None else 0
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
            return robj[0]
        elif col == 1:
            try:
                return robj[1].upper() + (" (!)" if robj[1] != robj[2] else "")
            except AttributeError:
                return "None (!)"
        elif col == 2:
            return robj[2].upper()

    def sort(self, column, order=QtCore.Qt.AscendingOrder):
        rev = not (order == QtCore.Qt.AscendingOrder)
        self.beginResetModel()
        self.l.sort(key=lambda i: i[column], reverse=rev)
        self.endResetModel()

    def flags(self, index):
        q = QtCore.Qt
        return q.ItemIsSelectable | q.ItemIsEnabled

    def headerData(self, col, orientation, role):
        if (orientation == QtCore.Qt.Horizontal and
                role == QtCore.Qt.DisplayRole):
            return self.headerdata[col]
        else:
            return None

    def numItems(self):
        return len(self.l)

    def replaceContents(self, newList):
        self.beginResetModel()
        self.l = newList
        self.endResetModel()
