# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2015 Soren Bjornstad. All rights reserved.

import traceback

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QDialog, QInputDialog, QMessageBox, QShortcut, \
     QKeySequence, QFileDialog
from PyQt4.QtCore import QObject, QAbstractTableModel, QModelIndex
from ui.forms.students import Ui_Dialog

import ui.utils as utils
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

    def sort(self, column, order=QtCore.Qt.AscendingOrder):
        rev = (order == QtCore.Qt.AscendingOrder)
        if column == 0:
            key = lambda i: i.getLn()
        elif column == 1:
            key = lambda i: i.getFn()
        elif column == 2:
            key = lambda i: i.getTpid()
        elif column == 3:
            key = lambda i: i.getTpdev()
        elif column == 4:
            key = lambda i: i.getEmail()

        self.beginResetModel()
        self.l.sort(key=key, reverse=rev)
        self.endResetModel()

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

    def setNextClassInsert(self, cls):
        """
        Since insertRows() does not accept custom arguments, this sets the
        class to be used for the dummy entry when a new addition is made.
        """
        self.nextClassInsert = cls

    def insertRows(self, row, count, parent=QModelIndex()):
        """
        Insert one or more new rows. Before calling, make sure to
        setNextClassInsert() so that the new dummy entry is in the correct
        class.
        """

        insertion = db.students.newDummyTextStudent(self.nextClassInsert)
        self.beginInsertRows(parent, row, row+count-1)
        for i in range(count):
            self.l.insert(int(row + i), insertion)
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
        self.form.fastEditBox.toggled.connect(self.onChangeFastEdit)
        self.onChangeFastEdit() # set up initial state

        self.setupClassCombo()
        self.tableModel = StudentTableModel(self)
        self.form.tableView.setModel(self.tableModel)
        self.reFillStudents()
        self.form.classCombo.activated.connect(self.reFillStudents)

        qlShortcut = QShortcut(QKeySequence("Alt+L"), self.form.tableView)
        qlShortcut.connect(qlShortcut, QtCore.SIGNAL("activated()"), lambda: self.form.tableView.setFocus())

    def setInitialClass(self, cls):
        idx = self.form.classCombo.findText(cls.getName())
        self.form.classCombo.setCurrentIndex(idx)
        self.reFillStudents()

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
        self.defaultSort()

    def defaultSort(self):
        self.form.tableView.sortByColumn(0)

    def onAdd(self):
        self.tableModel.setNextClassInsert(self._currentClass())
        self.tableModel.insertRow(len(self.tableModel.l))
        idx = self.tableModel.createIndex(len(self.tableModel.l)-1, 0)
        self.form.tableView.setFocus()
        self.form.tableView.setCurrentIndex(idx)
        self.form.tableView.edit(idx)

    def onDelete(self):
        if not self.fastEdit:
            resp = utils.confirmDeleteBox('student')
            if resp != 16384:
                return
        self.tableModel.removeRow(self.form.tableView.currentIndex().row())
    def onImport(self):
        f = QFileDialog.getOpenFileName(caption="Import Students from CSV",
                filter="All files (*)")
        if not f:
            return
        importer = db.students.StudentImporter(f, self._currentClass())
        errors = importer.txtImport()

        self.reFillStudents()

        if errors:
            utils.tracebackBox("Import returned the following errors:\n%s\n\nAny " \
                               "students that were valid have been imported." \
                               % errors, "Import Results", False)
        else:
            utils.informationBox("Import completed successfully.",
                                 "Import Results")

    def onExport(self):
        filename = QFileDialog.getSaveFileName(
                caption="Import Students from CSV", filter="All files (*)")
        if not filename:
            return

        try:
            db.students.exportCsv(db.students.studentsInClass(
                        self._currentClass()), filename)
        except Exception as e:
            utils.tracebackBox("Could not write to the location specified. "
                               "The original error is as follows:\n\n"
                               "%s" % traceback.format_exc(),
                               title="Export Failed",
                               includeErrorBoilerplate=False)
        else:
            utils.informationBox("Export completed successfully.",
                                 "Export Results")


    def onChangeFastEdit(self):
        self.fastEdit = self.form.fastEditBox.isChecked()
        if self.fastEdit:
            self.form.addButton.setDefault(True)
        else:
            self.form.addButton.setDefault(False)

    def _currentClass(self):
        clsName = unicode(self.form.classCombo.currentText())
        cls = db.classes.getClassByName(clsName)
        return cls
