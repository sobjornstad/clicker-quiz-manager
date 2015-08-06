# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2015 Soren Bjornstad. All rights reserved.

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QDialog, QInputDialog, QMessageBox, QShortcut, \
     QKeySequence, QFileDialog
from PyQt4.QtCore import QObject, QAbstractTableModel, QModelIndex
from ui.forms.history import Ui_Dialog

import ui.utils as utils
import db.genquiz

class HistoryDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self)
        self.form = Ui_Dialog()
        self.form.setupUi(self)

        #self.form.addButton.clicked.connect(self.onAdd)
        #self.form.deleteButton.clicked.connect(self.onDelete)
        #self.form.importButton.clicked.connect(self.onImport)
        #self.form.exportButton.clicked.connect(self.onExport)
        #self.form.closeButton.clicked.connect(self.reject)
        #self.form.fastEditBox.toggled.connect(self.onChangeFastEdit)
        #self.onChangeFastEdit() # set up initial state

        #self.setupClassCombo()
        #self.tableModel = StudentTableModel(self)
        #self.form.tableView.setModel(self.tableModel)
        #self.reFillStudents()
        #self.form.classCombo.activated.connect(self.reFillStudents)

        #self.tableModel.rowsRemoved.connect(self._updateStudentTotal)
        #self.tableModel.rowsInserted.connect(self._updateStudentTotal)
        #self.tableModel.modelReset.connect(self._updateStudentTotal)
        #self._updateStudentTotal()

        #qlShortcut = QShortcut(QKeySequence("Alt+L"), self.form.tableView)
        #qlShortcut.connect(qlShortcut, QtCore.SIGNAL("activated()"), lambda: self.form.tableView.setFocus())
