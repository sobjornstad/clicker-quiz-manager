# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2015 Soren Bjornstad. All rights reserved.

from PyQt4.QtGui import QDialog
from forms.prefs import Ui_Dialog
import utils

class PrefsDialog(QDialog):
    def __init__(self, mw):
        QDialog.__init__(self)
        self.mw = mw
        self.form = Ui_Dialog()
        self.form.setupUi(self)
        self.restartSuggested = False
        self.options = {}
        self.setupPrefsState()

        self.form.cancelButton.clicked.connect(self.reject)
        self.form.okButton.clicked.connect(self.dumpPrefsState)

    def markRestartRequired(self):
        self.restartSuggested = True

    def setupPrefsState(self):
        conf = self.mw.config

        self.options['debugMode'] = conf.readConf('debugMode').toBool()
        self.options['autoAnsA'] = conf.readConf('autoAnsA').toBool()
        self.options['saveInterval'] = conf.readConf('saveInterval').toInt()[0]

        # note: don't use setCheckState(), that makes a tri-state box!
        self.form.debugMode.setChecked(self.options['debugMode'])
        self.form.autoAnsA.setChecked(self.options['autoAnsA'])
        self.form.saveInterval.setValue(self.options['saveInterval'])

    def dumpPrefsState(self):
        conf = self.mw.config

        newDebug = self.form.debugMode.isChecked()
        if newDebug != self.options['debugMode']:
            self.markRestartRequired()
            conf.writeConf('debugMode', newDebug)

        newSaveInterval = self.form.saveInterval.value()
        if newSaveInterval != self.options['saveInterval']:
            self.markRestartRequired()
            conf.writeConf('saveInterval', newSaveInterval)

        newAutoAnsA = self.form.autoAnsA.isChecked()
        if newAutoAnsA != self.options['autoAnsA']:
            self.markRestartRequired() # not really, if this were coded properly
            conf.writeConf('autoAnsA', newAutoAnsA)

        self.accept()
        if self.restartSuggested:
            utils.informationBox("The changes will take effect when you " \
                    "restart CQM.", "Restart Required")
