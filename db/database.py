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
        self.auxConnection = None
        inter = self
        self._defaultCursor.execute('PRAGMA foreign_keys = ON')
        self._defaultCursor.execute('PRAGMA foreign_keys')
        assert self._defaultCursor.fetchall()[0][0] == 1, \
                "CQM cannot run without foreign key constraints available. "\
                "Please contact the developer for more information."

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
        Execute /query/ with /parameters/ and return the cursor. If this raises
        a threading error, try executing with the auxiliary connection instead.
        (Before that works, you have to start a new connection with
        self.takeOutNewConnection().)
        """

        try:
            if parameters is not None:
                self._defaultCursor.execute(query, parameters)
            else:
                self._defaultCursor.execute(query)
        except sqlite.ProgrammingError as e:
            if ('created in a thread' in str(e) or
                'Recursive use' in str(e)):
                assert self.auxConnection is not None, \
                        "You must take out a new connection before accessing " \
                        "the db from another thread!"
                cursor = self.auxConnection.cursor()
                if parameters is not None:
                    cursor.execute(query, parameters)
                else:
                    cursor.execute(query)
                return cursor
            else:
                # don't mask unrelated errors
                raise
        else:
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
            self.forceSave()
            return True
        else:
            return False

    def forceSave(self):
        """Force a commit and update last save time."""

        # similar structure to exQuery()
        try:
            self._defaultConnection.commit()
        except sqlite.ProgrammingError as e:
            if ('created in a thread' in str(e) or
                'Recursive use' in str(e)):
                assert self.auxConnection is not None, \
                        "You must take out a new connection before accessing " \
                        "the db from another thread!"
                self.auxConnection.commit()
            else:
                raise
        self._lastSavedTime = time.time()


    def takeOutNewConnection(self):
        """
        Open an alternate connection for use in a worker thread. Note that
        this only supports a single alternate connection, but we are not using
        multi-threading in a very complicated way here, so this should not be
        a problem.

        When done with this connection (e.g., when the thread terminates or is
        otherwise done with db access), make sure to run
        closeAuxiliaryConnection() to preserve the auxiliary connection slot
        for another thread.
        
        Raises AssertionError if the database was not opened with a filename
        (because it's not possible to open multiple connections to a database
        that's in memory), or if an auxiliary connection already exists,
        likely indicating attempted concurrent access from more than two
        threads, or another programming error.

        NOTE: I was getting segfaults when I tried to *write* to the database
        with this connection. I don't know what I might have been doing wrong,
        but since I rewrote the class (it didn't need to do a write anyway), I
        haven't seen that happening. If in the future we want to be able to
        write to the db from a different thread, we may have to deal with it
        again.
        """
        assert self._fname is not None, "Auxiliary connections cannot be " \
                "used with in-memory databases!"
        assert self.auxConnection is None, \
                "An auxiliary connection already exists! was %r" % (
                        self.auxConnection)
        self.auxConnection = sqlite.connect(self._fname)

    def closeAuxiliaryConnection(self):
        if self.auxConnection is not None:
            self.auxConnection.commit()
            self.auxConnection.close()
            self.auxConnection = None
