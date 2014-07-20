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
        self.sl = db.sets.getAllSets()
        for s in self.sl:
            self.form.setList.addItem(s.getName())

    def add(self):
        toAdd, didEnter = QInputDialog.getText(self, "Add Set",
                 "What do you want to call the new set?")
        toAdd = str(toAdd)

        if not didEnter:
            return
        if not toAdd:
            utils.errorBox("You must enter a name for the set.",
                    "No name provided")
            return
        if db.sets.isDupe(toAdd):
            utils.errorBox("You already have a set by that name.",
                    "Duplicate Entry")
            return

        self.form.setList.addItem(toAdd)
        num = self.form.setList.count() - 1 # row numbering starts from 0
        db.sets.Set(toAdd, num)

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
        db.sets.findSet(num=val).delete()
        self.form.setList.takeItem(val)
        db.sets.shiftNums() # fill in gap in ordering

    def rename(self):
        # get new name and confirm change
        curItem = self.form.setList.currentItem()
        name = str(curItem.text())
        text, didEnter = QInputDialog.getText(self, "Rename Set",
                "Rename to:", text=name)
        if not didEnter:
            return
        if not text:
            utils.errorBox("You must enter a name for the set.",
                    "No name provided")
            return

        # check for dupes
        text = str(text)
        if db.sets.isDupe(text):
            utils.errorBox("You already have a set by that name.",
                    "Duplicate Entry")
            return

        # update state, db, and listbox
        rSet = db.sets.findSet(name=name)
        rSet.setName(text)
        curItem.setData(0, text)

    def moveUp(self):
        pass
    def moveDown(self):
        pass
