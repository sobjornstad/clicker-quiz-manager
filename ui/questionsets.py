from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QDialog, QMessageBox, QInputDialog
from forms.questionsets import Ui_Dialog

import utils

class QuestionSetsDialog(QDialog):
    def __init__(self, mw):
        QDialog.__init__(self)
        self.mw = mw
        self.form = Ui_Dialog()
        self.form.setupUi(self)

        self.form.addButton.clicked.connect(self.onAdd)
        self.form.editButton.clicked.connect(self.onEdit)
        self.form.deleteButton.clicked.connect(self.onDelete)
        self.form.closeButton.clicked.connect(self.accept)

        self.form.setList.addItem("Test Item")
        self.form.setList.itemDoubleClicked.connect(self.onEdit)

    def onAdd(self):
        inp = QInputDialog()
        inp.setLabelText("What do you want to call the new set?")
        inp.setWindowTitle("Add Set")
        inp.exec_()
        toAdd = inp.textValue()
        self.form.setList.addItem(toAdd)

    def onEdit(self):
        import editset
        se = editset.SetEditor(self)
        se.exec_()

    def onDelete(self):
        r = utils.confirmDeleteBox("set")
        if r == QMessageBox.Yes:
            val = self.form.setList.currentRow()
            self.form.setList.takeItem(val)
