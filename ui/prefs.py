# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2015 Soren Bjornstad. All rights reserved.

import pickle

import PyQt4.QtCore as QtCore
from PyQt4.QtGui import QDialog
from forms.prefs import Ui_Dialog
import utils

import db.database as d

class ConfigurationManager(object):
    """
    Stores general user preferences using QSettings.
    """
    def __init__(self):
        self.qs = QtCore.QSettings("562 Software", "CQM")
    def sync(self):
        self.qs.sync()

    def writeConf(self, key, value):
        "Write a *value* to the persistent config under key *key*."
        self.qs.setValue(key, value)
    def readConf(self, key, default=None):
        """
        Return a value from the persistent config stored under key *key*. In
        order to use the value usefully, you need to call its .toInt() or
        .toString() method (other conversions are available where appropriate --
        see docs or do dir(returnval)).

        If the key does not exist, a value of 0 or an empty string will be
        returned, respectively; keep that in mind when designing the values.
        """
        if default is not None:
            return self.qs.value(key, default)
        else:
            return self.qs.value(key)

    def allKeys(self):
        "Return Python list of all keys in existence."
        keys = self.qs.allKeys()
        return [str(i) for i in keys]

class DatabaseConfManager(QtCore.QObject):
    """
    Stores more specific things like email options in the conf table of the db.
    """
    def __init__(self, mw):
        self.mw = mw
        self.conf = None
        self.loadDb()

    def exists(self, key):
        """Return True if /key/ is defined in the configuration."""
        return self.conf.has_key(key)

    def get(self, key):
        """Return the value of /key/, or None if key doesn't exist."""
        return self.conf.get(key, None)

    def put(self, key, value):
        """
        Update internal configuration model with the new value /value/ for
        /key/. Since many put()s are often called in a row, you must explicitly
        call sync() to update the database with the changes.
        """
        if self.get(key) != value:
            self.conf[key] = value

    def loadDb(self):
        c = d.inter.exQuery('SELECT conf FROM conf')
        try:
            self.conf = pickle.loads(c.fetchall()[0][0])
        except (EOFError, IndexError):
            # no configuration initialized
            self.conf = {}

    def allKeys(self):
        return self.conf.keys()

    def sync(self):
        """
        Write current dictionary state out to the database.
        """
        d.inter.exQuery('UPDATE conf SET conf=?', (pickle.dumps(self.conf),))
        d.inter.checkAutosave()


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

    def changeLocalOrServer(self):
        doEnableLocal = self.form.localLatexRadio.isChecked()
        self.form.hostnameBox.setEnabled(not doEnableLocal)
        self.form.usernameBox.setEnabled(not doEnableLocal)
        self.form.passwordBox.setEnabled(not doEnableLocal)
        self.form.xelatexCommand.setEnabled(doEnableLocal)

    def markRestartRequired(self):
        self.restartSuggested = True

    def setupPrefsState(self):
        conf = self.mw.config
        dconf = self.mw.databaseConfig

        self.options['debugMode'] = conf.readConf('debugMode').toBool()
        self.options['autoAnsA'] = conf.readConf('autoAnsA').toBool()
        self.options['saveInterval'] = conf.readConf('saveInterval').toInt()[0]
        self.options['savePasswords'] = conf.readConf('savePasswords').toBool()
        self.options['latexexe'] = conf.readConf(
                'latexExecutable', 'xelatex').toString()
        self.options['localLatex'] = conf.readConf('localLatex', True).toBool()

        hn, us, sp = dconf.get('serverHostname'), dconf.get('serverUsername'), \
                dconf.get('serverPassword')
        self.options['serverHostname'] = hn if hn is not None else ""
        self.options['serverUsername'] = us if us is not None else ""
        self.options['serverPassword'] = sp if sp is not None else ""

        # note: don't use setCheckState(), that makes a tri-state box!
        self.form.debugMode.setChecked(self.options['debugMode'])
        self.form.autoAnsA.setChecked(self.options['autoAnsA'])
        self.form.saveInterval.setValue(self.options['saveInterval'])
        self.form.savePasswords.setChecked(self.options['savePasswords'])
        self.form.savePasswords.toggled.connect(self.onPasswordCheck)
        self.form.xelatexCommand.setText(self.options['latexexe'])
        self.form.hostnameBox.setText(self.options['serverHostname'])
        self.form.usernameBox.setText(self.options['serverUsername'])
        self.form.passwordBox.setText(self.options['serverPassword'])

        if self.options['localLatex']:
            self.form.localLatexRadio.setChecked(True)
        else:
            self.form.remoteLatexRadio.setChecked(True)
        self.form.localLatexRadio.toggled.connect(self.changeLocalOrServer)
        self.changeLocalOrServer()


    def dumpPrefsState(self):
        conf = self.mw.config
        dconf = self.mw.databaseConfig

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

        newSavePasswords = self.form.savePasswords.isChecked()
        if newSavePasswords != self.options['savePasswords']:
            conf.writeConf('savePasswords', newSavePasswords)

        newLocalLatex = self.form.localLatexRadio.isChecked()
        if newLocalLatex != self.options['localLatex']:
            conf.writeConf('localLatex', newLocalLatex)

        newLatex = unicode(self.form.xelatexCommand.text())
        if newLatex != self.options['latexexe']:
            conf.writeConf('latexExecutable', newLatex)

        newHostname = unicode(self.form.hostnameBox.text())
        if newHostname != self.options['serverHostname']:
            dconf.put('serverHostname', newHostname)

        newUsername = unicode(self.form.usernameBox.text())
        if newUsername != self.options['serverUsername']:
            dconf.put('serverUsername', newUsername)

        newPassword = unicode(self.form.passwordBox.text())
        if newPassword != self.options['serverPassword']:
            dconf.put('serverPassword', newPassword)

        conf.sync()
        dconf.sync()
        self.accept()
        if self.restartSuggested:
            utils.informationBox("The changes will take effect when you " \
                    "restart CQM.", "Restart Required")

    def onPasswordCheck(self):
        if self.form.savePasswords.isChecked():
            utils.warningBox("Please note: saving passwords may be too "
                    "insecure for some users. While saved passwords are never "
                    "accessible from CQM's interface, passwords are stored in "
                    "plain text, so it is possible for a "
                    "knowledgeable user with a copy of your database file to "
                    "extract the password from there. If this makes you "
                    "uncomfortable, please do not use this option.\n\n"
                    "You can clear saved passwords at any time by running "
                    "Tools -> Forget Saved Passwords.",
                    "Security advisory")
        else:
            utils.warningBox("Disabling password saving does not immediately "
                    "clear any passwords that are already saved. To do so, "
                    "please choose Tools -> Forget Saved Passwords.",
                    "Security advisory")

def wipeAllPasswords(manager):
    """
    Search through all keys available in DatabaseConfManager /manager/ for keys
    beginning with 'optionsForClass_' (indicating class email options), and
    wipe any saved passwords from them. Also wipe LaTeX server password. Then
    sync and save the database.
    """
    for key in manager.allKeys():
        if key.startswith('optionsForClass_'):
            oldVals = manager.get(key)
            oldVals['password'] = ''
            manager.put(key, oldVals)
        if key == 'serverPassword':
            manager.put(key, '')

    manager.sync()
    d.inter.forceSave()
