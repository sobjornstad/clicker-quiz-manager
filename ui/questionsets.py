# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2014 Soren Bjornstad. All rights reserved.

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QDialog, QMessageBox, QInputDialog, QShortcut, \
     QKeySequence
from forms.questionsets import Ui_Dialog

import utils
import db.sets
from db.questions import getBySet as getQuestionsBySet

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

        self.form.setList.model().rowsMoved.connect(self.onDragDrop)
        qlShortcut = QShortcut(QKeySequence("Alt+L"), self.form.setList)
        qlShortcut.connect(qlShortcut, QtCore.SIGNAL("activated()"), lambda: self.form.setList.setFocus())

        self.fillList()

    def fillList(self):
        "Fill sets window with sets stored in the db."
        self.sl = db.sets.getAllSets()
        for s in self.sl:
            self.form.setList.addItem(s.getName())

    def add(self):
        toAdd, didEnter = QInputDialog.getText(self, "Add Set",
                 "What do you want to call the new set?")
        toAdd = unicode(toAdd)

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
        db.sets.Set.createNew(toAdd, num)

    def edit(self):
        import editset
        se = editset.SetEditor(self)
        se.exec_()

    def delete(self):
        cRow = self.form.setList.currentRow()
        st = db.sets.findSet(num=cRow)
        numQuestions = len(getQuestionsBySet(st))
        r = utils.confirmDeleteBox("set",
                "The %i question%s in it will be deleted." %
                ( numQuestions, '' if numQuestions == 1 else 's'))
        if r != QMessageBox.Yes:
            return

        st.delete()
        db.sets.shiftNums() # fill in gap in ordering
        self.form.setList.takeItem(cRow)

    def rename(self):
        # get new name and confirm change
        curItem = self.form.setList.currentItem()
        name = unicode(curItem.text())
        text, didEnter = QInputDialog.getText(self, "Rename Set",
                "Rename to:", text=name)
        if not didEnter:
            return
        if not text:
            utils.errorBox("You must enter a name for the set.",
                    "No name provided")
            return
        if text == name:
            return # assume user meant to cancel

        # check for dupes
        text = unicode(text)
        if db.sets.isDupe(text):
            utils.errorBox("You already have a set by that name.",
                    "Duplicate Entry")
            return

        # update state, db, and listbox
        rSet = db.sets.findSet(name=name)
        rSet.setName(text)
        curItem.setData(0, text)

    def onDragDrop(self, start, end, parent, destination, row):
        "Basically copied from onDragDrop function in editset.py."
        mFrom = end
        mTo = row
        db.sets.insertSet(db.sets.findSet(num=mFrom), mTo)

    def moveUp(self):
        self.move('up')
    def moveDown(self):
        self.move('down')
    def move(self, direction):
        # what needs to be swapped?
        cRow = self.form.setList.currentRow()

        # make sure it can go that way
        maxRow = self.form.setList.count() - 1
        if (cRow == 0 and direction == 'up') or (
                cRow == maxRow and direction == 'down'):
            # assume the user will know what she did wrong; keep our mouth shut
            return

        # modify the db
        s1 = db.sets.findSet(num=cRow)
        s2 = db.sets.findSet(num=(cRow-1 if direction == 'up' else cRow+1))
        db.sets.swapRows(s1, s2)

        # update the list on-screen
        i = self.form.setList.takeItem(cRow)
        self.form.setList.insertItem(cRow-1 if direction == 'up' else cRow+1, i)
        self.form.setList.setCurrentRow(cRow-1 if direction == 'up' else cRow+1)
