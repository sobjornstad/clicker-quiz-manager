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

        self.tableModel = AnswersTableModel(self)
        self.form.stuAnswersTable.setModel(self.tableModel)

        qlShortcut = QShortcut(QKeySequence("Alt+L"), self.form.studentsTable)
        qlShortcut.connect(qlShortcut, QtCore.SIGNAL("activated()"), lambda: self.form.studentsTable.setFocus())

        self.setupStudentList()

    def setupStudentList(self):
        print self.cls
        students = db.students.studentsInClass(self.cls)
        # sort by last name, then first name
        students.sort(key=lambda i: i.getFn())
        students.sort(key=lambda i: i.getLn())
        for stu in students:
            self.form.studentsTable.addItem("%s, %s"%(stu.getLn(), stu.getFn()))


    def onViewQuiz(self):
        pass




class AnswersTableModel(QAbstractTableModel):
    def __init__(self, parent, l=[], *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.parent = parent
        self.l = l
        self.headerdata = ["#", "Answer", "Correct"]

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
            return robj[0]
        elif col == 1:
            return robj[1].upper()
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
