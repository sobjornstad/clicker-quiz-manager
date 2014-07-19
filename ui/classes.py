from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QDialog, QInputDialog, QMessageBox
from PyQt4.QtCore import QObject
from forms.classes import Ui_dialog

import utils
import db.classes

class ClassesWindow(QDialog):
    def __init__(self, mw):
        QDialog.__init__(self)
        self.mw = mw
        self.form = Ui_dialog()
        self.form.setupUi(self)

        self.fillList()
        self.form.closeButton.clicked.connect(self.accept)
        self.form.addButton.clicked.connect(self.add)
        self.form.deleteButton.clicked.connect(self.delete)
        self.form.renameButton.clicked.connect(self.rename)

    def fillList(self):
        "Fill classes window with classes stored in the db."
        self.cl = db.classes.getAllClasses()
        for c in self.cl:
            self.form.listWidget.addItem(c.getName())

    def add(self):
        text, didEnter = QInputDialog.getText(self, "New Class", "Name:")
        if not didEnter:
            return
        if not text:
            utils.errorBox("You must enter a name for the class.",
                    "No name provided")
        text = str(text) # away from QString
        if db.classes.isDupe(text):
            utils.errorBox("You already have a class by that name.",
                    "Duplicate Entry")
        else:
            newClass = db.classes.Class(text) # create db entry
            self.form.listWidget.addItem(newClass.getName()) # add to list

    def rename(self):
        # get new name and confirm change
        curItem = self.form.listWidget.currentItem()
        name = str(curItem.text())
        text, didEnter = QInputDialog.getText(self, "Rename Class",
                "Rename to:", text=name)
        if not didEnter:
            return
        if not text:
            utils.errorBox("You must enter a name for the class.",
                    "No name provided")
        text = str(text)

        # update state, db, and listbox
        rClass = db.classes.getClassByName(name)
        rClass.setName(text)
        curItem.setData(0, text)



    def delete(self):
        classToDelete = self.form.listWidget.currentItem()
        nameToDelete = classToDelete.text()
        resp = utils.confirmDeleteBox("class",
                "This will delete all associated quiz history for the class " \
                "\"%s\"! Your sets and questions will be unaffected." \
                % nameToDelete)

        if resp == 16384: # "yes"
            row = self.form.listWidget.currentRow()
            self.form.listWidget.takeItem(row)
            db.classes.deleteClass(nameToDelete)
