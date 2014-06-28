from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QDialog, QMessageBox
from PyQt4.QtCore import QObject

def informationBox(text, title=None):
    msgBox = QMessageBox()
    msgBox.setText(text)
    msgBox.setIcon(QtGui.QMessageBox.Information)
    if title:
        msgBox.setWindowTitle(title)
    msgBox.exec_()

def confirmDeleteBox(item):
    msgBox = QMessageBox()
    s = "Are you sure you want to delete this %s?" % item
    msgBox.setText(s)
    msgBox.setIcon(QMessageBox.Question)
    msgBox.setWindowTitle("Delete %s" % item.title())
    msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msgBox.setDefaultButton(QMessageBox.No)
    return msgBox.exec_()
