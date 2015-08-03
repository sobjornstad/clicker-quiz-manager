# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2015 Soren Bjornstad. All rights reserved.

import database as d
import db.classes

class Student(object):
    def __init__(self, stid):
        q = 'SELECT ln, fn, tpid, tpdev, email, cid FROM students WHERE stid=?'
        d.cursor.execute(q, (stid,))
        self._ln, self._fn, self._tpid, self._tpdev, self._email, cid = \
                d.cursor.fetchall()[0]
        self._class = db.classes.getClassByCid(cid)
        self._stid = stid

    @classmethod
    def createNew(cls, ln, fn, tpid, tpdev, email, class_):
        q = '''INSERT INTO students (stid, ln, fn, tpid, tpdev, email, cid)
               VALUES (null, ?, ?, ?, ?, ?, ?)'''
        d.cursor.execute(q, (ln, fn, tpid, tpdev, email, class_.getCid()))
        return cls(d.cursor.lastrowid)

    def dump(self):
        q = '''UPDATE students
               SET ln=:ln, fn=:fn, tpid=:tpid, tpdev=:tpdev,
                   email=:email, cid=:cid
               WHERE stid=:stid'''
        vals = {
                'stid':  self._stid,
                'ln':    self._ln,
                'fn':    self._fn,
                'tpid':  self._tpid,
                'tpdev': self._tpdev,
                'email': self._email,
                'cid': self._class.getCid()
               }
        d.cursor.execute(q, vals)
        d.checkAutosave()

    def __eq__(self, other):
        return (self._ln == other._ln and self._fn == other._fn and
                self._tpid == other._tpid and self._tpdev == other._tpdev and
                self._email == other._email and self._stid == other._stid and
                self._class == other._class)

    def __ne__(self, other):
        return not self.__eq__(self, other)

    def getStid(self):
        return self._stid
    def getLn(self):
        return self._ln
    def getFn(self):
        return self._fn
    def getTpid(self):
        return self._tpid
    def getTpdev(self):
        return self._tpdev
    def getEmail(self):
        return self._email
    def getClass(self):
        return self._class

    def setLn(self, ln):
        if self._ln != ln:
            self._ln = ln
            self.dump()
    def setFn(self, fn):
        if self._fn != fn:
            self._fn = fn
            self.dump()
    def setTpid(self, tpid):
        if self._tpid != tpid:
            self._tpid = tpid
            self.dump()
    def setTpdev(self, tpdev):
        if self._tpdev != tpdev:
            self._tpdev = tpdev
            self.dump()
    def setEmail(self, email):
        if self._email != email:
            self._email = email
            self.dump()

    def csvRepr(self):
        """
        Return a tab-separated representation of the data of this student
        (excluding the class, as we only export one class at a time).
        """
        s = '\t'.join([self._ln, self._fn, self._tpid, self._tpdev, self._email])
        return s

def makesDupeStudent(ln, fn, tpid, tpdev, email, class_):
    cid = class_.getCid()
    q = '''SELECT stid FROM students
           WHERE ln=? AND fn=? AND tpid=? AND tpdev=? AND email=? AND cid=?'''
    d.cursor.execute(q, (ln, fn, tpid, tpdev, email, cid))
    return (len(d.cursor.fetchall()) > 0)

def allStudents():
    """Return a list of all students."""
    d.cursor.execute('SELECT stid FROM students')
    return [Student(stu[0]) for stu in d.cursor.fetchall()]

def studentsInClass(cls):
    d.cursor.execute('SELECT stid FROM students WHERE cid=?', (cls.getCid(),))
    return [Student(stu[0]) for stu in d.cursor.fetchall()]

def newDummyTextStudent(cls):
    """
    Return a valid Student object, not a duplicate of any existing student,
    which contains dummy text to be filled in by the user. The student will be
    placed in the class specified.
    """

    ln = "Doe "
    fn = "Jane"
    tpid = "###"
    tpdev = "xxx"
    email = "email@example.com"

    num = 1
    while makesDupeStudent(ln + str(num), fn, tpid, tpdev, email, cls):
        num += 1
    return Student.createNew(ln + str(num), fn, tpid, tpdev, email, cls)
