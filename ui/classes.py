from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QDialog, QMessageBox
from PyQt4.QtCore import QObject
from forms.classes import Ui_dialog

import utils

class ClassesWindow(QDialog):
    def __init__(self, mw):
        QDialog.__init__(self)
        self.mw = mw
        self.form = Ui_dialog()
        self.form.setupUi(self)

        self.form.closeButton.clicked.connect(self.accept)
        self.form.addButton.clicked.connect(self.add)
        self.form.deleteButton.clicked.connect(self.delete)

    def add(self):
        utils.informationBox("Add button activated", "Button Clicked")

    def delete(self):
        utils.informationBox("Delete button activated", "Button Clicked")
