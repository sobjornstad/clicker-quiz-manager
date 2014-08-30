# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2014 Soren Bjornstad. All rights reserved.

import database as d

class Class(object):
    def __init__(self, name, cid=None):
        self._name = name
        self._cid = cid
        self.dump()

    def __eq__(self, other):
        return self._cid == other._cid and self._name == other._name

    def __ne__(self, other):
        return not self.__eq__(self, other)

    def getName(self):
        return self._name
    def getCid(self):
        return self._cid
    def setName(self, name):
        self._name = name
        self.dump()

    def dump(self):
        if self._cid:
            # exists already
            d.cursor.execute('UPDATE classes SET name=? WHERE cid=?',
                    (self._name, self._cid))
        else:
            # new set, not in db
            d.cursor.execute('INSERT INTO classes (name,setsUsed) VALUES (?,?)',
                    (self._name, 0))
            self._cid = d.cursor.lastrowid

        # at some point we will want to eliminate this for performance reasons;
        # just leaving it here to make sure things are consistent for now
        d.connection.commit()

def isDupe(name=None, cid=None):
    if cid and getClassByCid(cid): # guarded
        return True
    if name and getClassByName(name):
        return True
    return False

def getClassByCid(cid):
    """Return a Class from the db when given the cid. Return None if it doesn't
    exist."""

    d.cursor.execute('SELECT name FROM classes WHERE cid=?', (cid,))
    try:
        name = d.cursor.fetchall()[0][0]
    except IndexError:
        return None
    else:
        return Class(name, cid)

def getClassByName(name):
    """Return the first Class from the db by a given name when given the name.
    Return None if it doesn't exist."""

    d.cursor.execute('SELECT cid FROM classes WHERE name=?', (name,))
    try:
        cid = d.cursor.fetchall()[0][0]
    except IndexError:
        return None
    else:
        return Class(name, cid)

def getAllClasses():
    """Return a list of all classes in the database, in alphabetical order."""

    d.cursor.execute('SELECT cid, name FROM classes ORDER BY name')
    return [getClassByCid(i[0]) for i in d.cursor.fetchall()]

def deleteClass(name):
    name = str(name) # dumb QStrings
    cid = getClassByName(name).getCid()
    #TODO: When history is in place, we need to delete that
    d.cursor.execute('DELETE FROM classes WHERE cid=?', (cid,))
    d.connection.commit()
    #TODO: Cause the class to raise some kind of error if we try to use it

#TOTEST: Dupe names, deletion
