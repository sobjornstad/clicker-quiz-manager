from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QDialog, QMessageBox, QInputDialog
from forms.editset import Ui_Dialog

import utils

class SetEditor(QDialog):
    def __init__(self, setList):
        QDialog.__init__(self)
        self.sl = setList
        self.form = Ui_Dialog()
        self.form.setupUi(self)

        self.populateSets()

        self.form.addButton.clicked.connect(self.onAdd)
        self.form.deleteButton.clicked.connect(self.onDelete)
        self.form.importButton.clicked.connect(self.onImport)
        self.form.exportButton.clicked.connect(self.onExport)
        self.form.moveDownButton.clicked.connect(self.onMoveDown)
        self.form.moveUpButton.clicked.connect(self.onMoveUp)
        self.form.closeButton.clicked.connect(self.accept)

    def populateSets(self):
        # add all sets to set list; for now, add test
        j = self.sl.form.setList.currentItem().text()
        self.form.jumpCombo.addItem(j)

        # end test code
        txt = self.sl.form.setList.currentItem().text()
        i = self.form.jumpCombo.findText(txt)
        self.form.jumpCombo.setCurrentIndex(i)

    def onAdd(self):
        nqText = "New Question"
        self.form.questionList.addItem(nqText)
        self.form.questionList.findItems(nqText,
                QtCore.Qt.MatchExactly)[0].setSelected(True)

        self.form.questionBox.setFocus()

    def onDelete(self):
        pass

    def onImport(self):
        utils.informationBox("This feature is not implemented yet.", "Sorry!")

    def onExport(self):
        utils.informationBox("This feature is not implemented yet.", "Sorry!")

    def onMoveDown(self):
        pass

    def onMoveUp(self):
        pass