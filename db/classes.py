# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2014-2015 Soren Bjornstad. All rights reserved.

"""
Provides the Class class (sorry, that's a little ugly) and associated functions.

Functions:
    isDupe(name=None, cid=None): Determine if new values duplicate a Class.
    getClassByCid(cid): Get a Class given the cid.
    getClassByName(name): Get a Class given the name (Class names are unique).
    getAllClasses(): Get a list of all Classes in this db.
    deleteClass(name): Delete a class from the db (doesn't touch the object).

Abbreviations used in this module:
    cid: Class ID, the primary key for classes.

Class db schema:
    cid: integer primary key
    name: class name
    setsUsed: a parameter used in scheduling and not accessed through this
    module.
"""

import db.database as d

class Class(object):
    """
    Represents one class that the user is teaching. A class contains its own
    set of students and quiz history; a class does NOT constrain the available
    questions.

    All access to parameters should be done through the get/set methods so that
    the database stays in sync with the object state (changes are automatically
    written to the current transaction when a set() method is called).

    Public methods:
        getName()
        getCid()
        setName()
    """

    def __init__(self, cid):
        c = d.inter.exQuery('SELECT name FROM classes WHERE cid=?', (cid,))
        self._name = c.fetchall()[0][0]
        self._cid = cid

    @classmethod
    def createNew(cls, name):
        q = '''INSERT INTO classes (name, setsUsed) VALUES (?, 0)'''
        d.inter.exQuery(q, (name,))
        return cls(d.inter.getLastRowId())

    def __eq__(self, other):
        return (self.getCid() == other.getCid() and
                self.getName() == other.getName())

    def __ne__(self, other):
        return not self.__eq__(other)

    def getName(self):
        return self._name
    def getCid(self):
        return self._cid
    def setName(self, name):
        self._name = name
        self._dump()

    def _dump(self):
        "Dump changed object to the db."
        ####### following line causes segfault
        d.inter.exQuery('UPDATE classes SET name=? WHERE cid=?',
                (self._name, self._cid))
        d.inter.checkAutosave()


def isDupe(name=None, cid=None):
    """
    Return True if the given /name/ and /cid/ would create a duplicate if
    inserted into the database.
    """
    if cid and getClassByCid(cid): # guarded
        return True
    if name and getClassByName(name):
        return True
    return False

def getClassByCid(cid):
    """
    Return a Class from the db when given the cid. Return None if it doesn't
    exist.
    """
    c = d.inter.exQuery('SELECT name FROM classes WHERE cid=?', (cid,))
    try:
        name = c.fetchall()[0][0]
    except IndexError:
        return None
    else:
        return Class(cid)

def getClassByName(name):
    """
    Return the first Class from the db by a given name when given the name.
    Return None if it doesn't exist.
    """
    c = d.inter.exQuery('SELECT cid FROM classes WHERE name=?', (name,))
    try:
        cid = c.fetchall()[0][0]
    except IndexError:
        return None
    else:
        return Class(cid)

def getAllClasses():
    """Return a list of all classes in the database, in alphabetical order."""

    c = d.inter.exQuery('SELECT cid FROM classes ORDER BY name')
    return [Class(i[0]) for i in c.fetchall()]

def deleteClass(name):
    """
    Delete a class from the database; no return.

    TODO:
    This function should also take care of deleting class history, but this is
    not currently done because class history doesn't exist yet.
    """
    name = str(name) # dumb QStrings
    cid = getClassByName(name).getCid()
    d.inter.exQuery('DELETE FROM classes WHERE cid=?', (cid,))
    d.inter.checkAutosave()

#to test: Dupe names, deletion
