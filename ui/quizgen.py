from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QDialog, QMessageBox
from PyQt4.QtCore import QObject
from forms.quizgen import Ui_Dialog

import utils

class QuizWindow(QDialog):
    def __init__(self, mw):
        QDialog.__init__(self)
        self.mw = mw
        self.form = Ui_Dialog()
        self.form.setupUi(self)

        self.form.okButton.clicked.connect(self.accept)
        self.form.cancelButton.clicked.connect(self.reject)
        self.form.historyButton.clicked.connect(self.onHistory)

        self.setDefaultSpinValues()
        self.updateDueValues()
        self.populateComboBoxes()

    def populateComboBoxes(self):
        self.form.setCombo.addItem("Dummy option 1")
        self.form.setCombo.addItem("Dummy option 2")
        self.form.classCombo.addItem("Dummy option 1")
        self.form.classCombo.addItem("Dummy option 2")

    def updateDueValues(self):
        self.form.reviewDisplay.setText("(%i sets due)" % (5))
        self.form.newDisplay.setText("(%i available)" % (15))

    def setDefaultSpinValues(self):
        self.form.revQuestions.setValue(5)
        newQAvailable = 15
        self.form.newQuestions.setValue(newQAvailable)
        self.form.newQuestions.setMaximum(newQAvailable)

    def accept(self):
        QDialog.accept(self)

    def reject(self):
        QDialog.reject(self)

    def onHistory(self):
        utils.informationBox("History button activated", "Button Clicked")
