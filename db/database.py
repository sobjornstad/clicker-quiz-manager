# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2014-2015 Soren Bjornstad. All rights reserved.

"""
Provides access for other modules to the sqlite database.

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

# Every option besides making these global module variables seems needlessly
# complex.
# pylint: disable=C0103
# pylint: disable=W0603
connection = None
cursor = None
_lastSavedTime = None
_saveInterval = 60

def connect(fname, autosaveInterval=60):
    """
    Connect to database /fname/. Optionally, set the number of seconds between
    autosaves while this connection is open; if the time since the last commit
    is greater than this interval when checkAutosave() is called, a new commit
    will be made.
    """
    global connection, cursor, _lastSavedTime, _saveInterval
    connection = sqlite.connect(fname)
    cursor = connection.cursor()
    _lastSavedTime = time.time()
    _saveInterval = autosaveInterval

def openDbConnect(conn):
    """
    Pull an open connection into the database module's namespace for access by
    other parts of the program. This is useful in cases like running tests by
    creating a database in RAM (such that you can't run create_database
    separately and then reopen the connection).

    Example:
        >>> conn = db.tools.create_database.makeDatabase(':memory:')
        >>> db.database.openDbConnect(conn)
        >>> db.database.connection.commit()
    """

    global connection, cursor, _lastSavedTime
    connection = conn
    cursor = connection.cursor()
    _lastSavedTime = time.time()

def close():
    """Save and close database connection."""
    forceSave()
    connection.close()

def checkAutosave(thresholdSeconds=None):
    """
    Check when the last save (or database creation) was. If greater than
    /thresholdSeconds/, do a commit. If a commit is made, reset last save
    timer. _saveInterval, used unless a different value is passed, is set by a
    user preference on start.

    Return: True if a commit was completed, False if not time yet.
    """

    if thresholdSeconds == None:
        thresholdSeconds = _saveInterval

    global _lastSavedTime
    now = time.time()
    if now - _lastSavedTime > thresholdSeconds:
        connection.commit()
        _lastSavedTime = time.time()
        return True
    else:
        return False

def forceSave():
    """Force a commit and update last save time."""
    global _lastSavedTime
    connection.commit()
    _lastSavedTime = time.time()
