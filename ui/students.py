# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2015 Soren Bjornstad. All rights reserved.

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QDialog, QInputDialog, QMessageBox, QShortcut, \
     QKeySequence
from PyQt4.QtCore import QObject, QAbstractTableModel, QModelIndex
from forms.students import Ui_Dialog

import utils
import db.students
import db.classes

class StudentTableModel(QAbstractTableModel):
    def __init__(self, parent, l=[], *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.parent = parent
        self.l = l
        self.headerdata = ["Last", "First", "TP ID", "TP Device", "Email"]

    def rowCount(self, parent):
        return len(self.l)
    def columnCount(self, parent):
        return len(self.headerdata)

    def data(self, index, role):
        if not index.isValid():
            return None
        if not (role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole):
            # without including EditRole, the whole cell gets wiped out when
            # an edit is begun
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

    def setData(self, index, value, role):
        colNum = index.column()
        studentNum = index.row()
        robj = self.l[studentNum]
        value = unicode(value.toString())

        if colNum == 0:
            robj.setLn(value)
        elif colNum == 1:
            robj.setFn(value)
        elif colNum == 2:
            robj.setTpid(value)
        elif colNum == 3:
            robj.setTpdev(value)
        elif colNum == 4:
            robj.setEmail(value)

        self.emit(QtCore.SIGNAL("dataChanged"))
        return True

    def flags(self, index):
        q = QtCore.Qt
        return q.ItemIsSelectable | q.ItemIsEnabled | q.ItemIsEditable

    def headerData(self, col, orientation, role):
        if (orientation == QtCore.Qt.Horizontal and
                role == QtCore.Qt.DisplayRole):
            return self.headerdata[col]
        else:
            return None

    def replaceStudentSet(self, newList):
        self.l = newList
        self.reset()

    def addBlankStudent(self, cls):
        """
        Create a new blank student with dummy data. Return an index that can
        be used to select the first column of the new student.
        """

        # for the life of me, I cannot correctly implement insertRows, so I'm
        # doing this instead. Since I want to select something new after an
        # add it's ok that the selection breaks
        self.l.append(db.students.newDummyTextStudent(cls))
        self.beginResetModel()
        self.reset()
        self.endResetModel()
        return self.createIndex(len(self.l)-1, 0)

    def setNextClassInsert(self, cls):
        self.nextClassInsert = cls

    def insertRows(self, row, count, parent=QModelIndex()):
        """
        Insert one or more new rows. This method should be accessed through
        addBlankStudent() to avoid creating empty rows that don't show up in
        the database.
        """

        insertion = db.students.newDummyTextStudent(self.nextClassInsert)
        self.beginInsertRows(parent, row, row+count-1)
        for i in range(count):
            self.l.insert(int(row + count), insertion)
        self.endInsertRows()
        return True

    def removeRows(self, row, count, parent=QModelIndex()):
        for i in range(count):
            self.l[row].delete()
        self.beginRemoveRows(parent, row, row+count-1)
        for i in range(count):
            del self.l[row + i]
        self.endRemoveRows()
        return True

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

        #### TODO RECIPE:
        #i = self.form.jumpCombo.findText(set)
        #self.form.jumpCombo.setCurrentIndex(i)

        qlShortcut = QShortcut(QKeySequence("Alt+L"), self.form.tableView)
        qlShortcut.connect(qlShortcut, QtCore.SIGNAL("activated()"), lambda: self.form.tableView.setFocus())

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

        cls = self._currentClass()
        students = db.students.studentsInClass(cls)
        self.tableModel.replaceStudentSet(students)

    def onAdd(self):
        self.tableModel.setNextClassInsert(self._currentClass())
        self.tableModel.insertRow(len(self.tableModel.l))
        idx = self.tableModel.createIndex(len(self.tableModel.l)-1, 0)
        self.form.tableView.setFocus()
        self.form.tableView.setCurrentIndex(idx)
        self.form.tableView.edit(idx)

    def onDelete(self):
        self.tableModel.removeRow(self.form.tableView.currentIndex().row())
    def onImport(self):
        pass
    def onExport(self):
        pass

    def _currentClass(self):
        clsName = unicode(self.form.classCombo.currentText())
        cls = db.classes.getClassByName(clsName)
        return cls
