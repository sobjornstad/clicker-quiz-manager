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

    def fillList(self):
        "Fill classes window with classes stored in the db."
        self.cl = db.classes.getAllClasses()
        for c in self.cl:
            self.form.listWidget.addItem(c.getName())

    def add(self):
        text = QInputDialog.getText(self, "New Class", "Name:")
        text = str(text[0]) # away from QString
        newClass = db.classes.Class(text)
        self.form.listWidget.addItem(newClass.getName())
        #TODO: prevent dupes

    def rename(self):
        pass

    def delete(self):
        classToDelete = self.form.listWidget.currentItem()
        nameToDelete = classToDelete.text()
        resp = utils.confirmDeleteBox("class", "This will delete all " \
                "associated quiz history! Your sets and questions will " \
                "be unaffected.")

        if resp == 16384: # "yes"
            row = self.form.listWidget.currentRow()
            self.form.listWidget.takeItem(row)
            db.classes.deleteClass(nameToDelete)
