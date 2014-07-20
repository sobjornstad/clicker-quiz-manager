from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QDialog, QMessageBox, QInputDialog
from forms.questionsets import Ui_Dialog

import utils
import db.sets

class QuestionSetsDialog(QDialog):
    def __init__(self, mw):
        QDialog.__init__(self)
        self.mw = mw
        self.form = Ui_Dialog()
        self.form.setupUi(self)

        self.form.addButton.clicked.connect(self.add)
        self.form.editButton.clicked.connect(self.edit)
        self.form.setList.itemDoubleClicked.connect(self.edit)
        self.form.deleteButton.clicked.connect(self.delete)
        self.form.renameButton.clicked.connect(self.rename)
        self.form.upButton.clicked.connect(self.moveUp)
        self.form.downButton.clicked.connect(self.moveDown)
        self.form.closeButton.clicked.connect(self.accept)

        self.fillList()

    def fillList(self):
        "Fill sets window with sets stored in the db."
        #TODO: Make sure these are aligned based on the nums
        self.sl = db.sets.getAllSets()
        for s in self.sl:
            self.form.setList.addItem(s.getName())

    def add(self):
        inp = QInputDialog()
        inp.setLabelText("What do you want to call the new set?")
        inp.setWindowTitle("Add Set")
        inp.exec_()
        toAdd = inp.textValue()

        self.form.setList.addItem(toAdd)
        num = self.form.setList.count() - 1 # row numbering starts from 0
        db.sets.Set(str(toAdd), num)

    def edit(self):
        import editset
        se = editset.SetEditor(self)
        se.exec_()

    def delete(self):
        r = utils.confirmDeleteBox("set",
                "Any questions associated with it will be deleted.")
        if r != QMessageBox.Yes:
            return

        val = self.form.setList.currentRow()
        print val
        item = self.form.setList.takeItem(val)
        db.sets.deleteSet(db.sets.findSet(num=val).getName())

    def rename(self):
        pass

    def moveUp(self):
        pass
    def moveDown(self):
        pass
