# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2015 Soren Bjornstad. All rights reserved.

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QDialog, QInputDialog, QMessageBox, QShortcut, \
     QKeySequence
from PyQt4.QtCore import QObject, QAbstractTableModel
from forms.students import Ui_Dialog

import utils
import db.students
import db.classes

class StudentTableModel(QAbstractTableModel):
    def __init__(self, parent, l=[], *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.l = l
        self.headerdata = ["Last", "First", "TP ID", "TP Device", "Email"]

    def rowCount(self, parent):
        return len(self.l)
    def columnCount(self, parent):
        return len(self.headerdata)

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != QtCore.Qt.DisplayRole:
            return None

        col = index.column()
        robj = self.l[index.row()]
        if col == 0:
            return robj.getLn()
        elif col == 1:
            return robj.getFn()
        elif col == 2:
            return robj.getTpid()
        elif col == 3:
            return robj.getTpdev()
        elif col == 4:
            return robj.getEmail()

    def headerData(self, col, orientation, role):
        if (orientation == QtCore.Qt.Horizontal and
                role == QtCore.Qt.DisplayRole):
            return self.headerdata[col]
        else:
            return None

    def replaceStudentSet(self, newList):
        self.l = newList
        self.reset()


class StudentsDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self)
        self.form = Ui_Dialog()
        self.form.setupUi(self)

        self.form.addButton.clicked.connect(self.onAdd)
        self.form.deleteButton.clicked.connect(self.onDelete)
        self.form.importButton.clicked.connect(self.onImport)
        self.form.exportButton.clicked.connect(self.onExport)
        self.form.closeButton.clicked.connect(self.reject)

        self.setupClassCombo()
        self.tableModel = StudentTableModel(self)
        self.form.tableView.setModel(self.tableModel)
        self.reFillStudents()
        self.form.classCombo.activated.connect(self.reFillStudents)

        #### TODO RECIPES:
        #i = self.form.jumpCombo.findText(set)
        #self.form.jumpCombo.setCurrentIndex(i)

        qlShortcut = QShortcut(QKeySequence("Alt+L"), self.form.tableView)
        qlShortcut.connect(qlShortcut, QtCore.SIGNAL("activated()"), lambda: self.form.listWidget.setFocus())

    def setupClassCombo(self):
        self.form.classCombo.clear()
        cl = db.classes.getAllClasses()
        for c in cl:
            self.form.classCombo.addItem(c.getName())

    def reFillStudents(self):
        """
        Fill or clear & re-fill the students table based on the current value
        of the class combo.
        """

        clsName = unicode(self.form.classCombo.currentText())
        cls = db.classes.getClassByName(clsName)
        students = db.students.studentsInClass(cls)
        self.tableModel.replaceStudentSet(students)

    def onAdd(self):
        pass
    def onDelete(self):
        pass
    def onImport(self):
        pass
    def onExport(self):
        pass
