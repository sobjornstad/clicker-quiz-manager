# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2014 Soren Bjornstad. All rights reserved.

import sqlite3 as sqlite
import time

connection = None
cursor = None
lastSavedTime = None

def connect(fname):
    global connection, cursor, lastSavedTime
    connection = sqlite.connect(fname)
    cursor = connection.cursor()
    lastSavedTime = time.time()

def openDbConnect(conn):
    """
    This function pulls an open connection into the database module's namespace
    for access by other parts of the program. This is useful in cases like
    running tests by creating a database in RAM (such that you can't run
    create_database separately and then reopen the connection).

    Example:
        >>> conn = db.tools.create_database.makeDatabase(':memory:')
        >>> db.database.openDbConnect(conn)
        >>> db.database.connection.commit()
    """

    global connection, cursor, lastSavedTime
    connection = conn
    cursor = connection.cursor()
    lastSavedTime = time.time()

def close():
    forceSave()
    connection.close()

def checkAutosave(thresholdSeconds=60):
    """
    Check when the last save (or database creation) was. If greater than
    *thresholdSeconds*, do a commit. If a commit is made, reset last save
    timer.

    Return: True if a commit was completed, False if not time yet.
    """

    global lastSavedTime
    now = time.time()
    if now - lastSavedTime > thresholdSeconds:
        connection.commit()
        lastSavedTime = time.time()
        return True
    else:
        return False
def forceSave():
    """Force a commit and update last save time."""
    global lastSavedTime
    connection.commit()
    lastSavedTime = time.time()
