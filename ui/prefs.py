# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2015 Soren Bjornstad. All rights reserved.

from PyQt4.QtGui import QDialog
from forms.prefs import Ui_Dialog

class PrefsDialog(QDialog):
    def __init__(self, mw):
        QDialog.__init__(self)
        self.mw = mw
        self.form = Ui_Dialog()
        self.form.setupUi(self)
        self.options = {}
        self.setupPrefsState()

        self.form.cancelButton.clicked.connect(self.reject)
        self.form.okButton.clicked.connect(self.dumpPrefsState)

    def setupPrefsState(self):
        conf = self.mw.config

        self.options['tooltips'] = conf.readConf('showTooltips').toBool()
        self.options['debugMode'] = conf.readConf('debugMode').toBool()
        self.options['saveInterval'] = conf.readConf('saveInterval').toInt()[0]

        self.form.showTooltips.setChecked(self.options['tooltips'])
        self.form.debugMode.setChecked(self.options['debugMode'])
        self.form.saveInterval.setValue(self.options['saveInterval'])

    def dumpPrefsState(self):
        conf = self.mw.config

        newTooltips = self.form.showTooltips.isChecked()
        if newTooltips != self.options['tooltips']:
            conf.writeConf('showTooltips', newTooltips)

        newDebug = self.form.debugMode.isChecked()
        if newDebug != self.options['debugMode']:
            conf.writeConf('debugMode', newDebug)

        newSaveInterval = self.form.saveInterval.value()
        if newSaveInterval != self.options['saveInterval']:
            conf.writeConf('saveInterval', newSaveInterval)

        self.accept()
