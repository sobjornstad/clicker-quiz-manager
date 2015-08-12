# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2014-2015 Soren Bjornstad. All rights reserved.

"""
Provides access for other modules to the sqlite database.
TODO: update docstring

Public module globals:
    cursor: the sqlite database cursor
    connection: the sqlite connection

Public functions:
    connect: initialize the database connection
    openDbConnect: link module to an already open database connection (testing)
    close: save any pending changes and close database connection
    checkAutosave: maybe commit, depending on time since last commit
    forceSave: commit all changes immediately

Note that initializing a *new* database is done in db/tools/create_database.py.
"""

import sqlite3 as sqlite
import time

# Every option besides making this a global module variable seems needlessly
# complex.
# pylint: disable=C0103
# pylint: disable=W0603
inter = None

class DatabaseInterface(object):
    def __init__(self, connection, filename=None, autosaveInterval=60):
        global inter
        self._defaultConnection = connection
        self._defaultCursor = self._defaultConnection.cursor()
        self._lastSavedTime = time.time()
        self._saveInterval = autosaveInterval
        self._fname = filename
        inter = self

    @classmethod
    def connectToFile(cls, fname, autosaveInterval=60):
        """
        Connect to database /fname/ and set that connection as the default
        connection. Optionally, set the number of seconds between autosaves
        while this connection is open; if the time since the last commit is
        greater than this interval when checkAutosave() is called, a new commit
        will be made.
        """
        newConnection = sqlite.connect(fname)
        return cls(newConnection, fname, autosaveInterval)

    def exQuery(self, query, parameters=None):
        """
        Execute /query/ with /parameters/ and return the cursor object.
        """

        if parameters is not None:
            self._defaultCursor.execute(query, parameters)
        else:
            self._defaultCursor.execute(query)
        return self._defaultCursor

    def getLastRowId(self):
        return self._defaultCursor.lastrowid

    def close(self):
        """Save and close database connection."""
        self.forceSave()
        self._defaultConnection.close()

    def checkAutosave(self, thresholdSeconds=None):
        """
        Check when the last save (or database creation) was. If greater than
        /thresholdSeconds/, do a commit. If a commit is made, reset last save
        timer.

        Return: True if a commit was completed, False if not time yet.
        """

        if thresholdSeconds == None:
            thresholdSeconds = self._saveInterval

        now = time.time()
        if now - self._lastSavedTime > thresholdSeconds:
            self._defaultConnection.commit()
            self._lastSavedTime = time.time()
            return True
        else:
            return False

    def forceSave(self):
        """Force a commit and update last save time."""
        self._defaultConnection.commit()
        self._lastSavedTime = time.time()

#def takeOutNewConnection():
#    """
#    Return an extra connection to the db to be used in an auxiliary thread,
#    using the filename of the database that's currently otherwise open. The
#    calling process is responsible for committing and closing the connection
#    when done with it.
#    """
#    auxConnection = sqlite.connect(_fname)
#    return auxConnection
