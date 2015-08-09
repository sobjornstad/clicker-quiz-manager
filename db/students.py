# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2015 Soren Bjornstad. All rights reserved.

import database as d
import db.classes
import csv

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

    def delete(self):
        #TODO: remove any quiz data, etc.
        d.cursor.execute('DELETE FROM students WHERE stid=?', (self._stid,))
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
        Return a comma-separated representation of the data of this student
        (excluding the class, as we only export one class at a time).

        Column order is ln, fn, tpid, tpdev, email -- where headers are added
        in the export function, they must match this order.
        """

        columns = [self._ln, self._fn, self._tpid, self._tpdev, self._email]
        # NOTE: It's impossible (as far as I can see) to escape double
        # quotation marks in a way that TurningPoint will accept. Not using
        # them could be a validation constraint if we later do student
        # validation.
        for column in range(len(columns)):
            if ',' in columns[column]:
                columns[column] = '"%s"' % columns[column]

        s = ','.join(columns)
        return s


### UTILITY FUNCTIONS ###
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

def findStudentByTpid(tpid, cls):
    """
    Return a Student matching tpid /tpid/ in class /cls/.

    Return:
        - If the tpid is valid, a Student object for that student.
        - If the tpid doesn't exist, None.
    
    Raises:
        AssertionError: If more than one student matches, we've screwed up,
        because tpids are required to be unique.
    """
    d.cursor.execute('SELECT stid FROM students WHERE tpid=?', (tpid,))
    retvals = d.cursor.fetchall()
    if not retvals:
        return None
    if len(retvals) > 1:
        assert False, "ERROR: Two students have the same tpid! Did we " \
                      "remember to implement validation?"
    return Student(retvals[0][0])

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


### EXPORTING ###
def exportCsv(studentList, filename):
    headers = 'Last Name,First Name,User ID, Device ID(s),Email'
    with open(filename, 'wb') as f:
        f.write(headers + '\r\n')
        for stu in studentList:
            f.write(stu.csvRepr() + '\r\n')


### IMPORTING ###
class ImporterError(Exception):
    def __init__(self, emsg):
        self.emsg = emsg
    def __str__(self):
        return repr(self.emsg)

class StudentImporter(object):
    def __init__(self, fname, cls):
        self.fname = fname
        self.cls = cls
        self.students = []
        self.errors = []

    def txtImport(self):
        """
        Run an import. Returns a string to display to the user containing a
        list of errors in the import. If headers are invalid, raise
        ImporterError.
        """

        with open(self.fname, 'rb') as csvfile:
            try:
                dialect = csv.Sniffer().sniff(csvfile.read(1024))
            except Exception as e:
                if "Could not determine delimiter" in e:
                    return "Could not determine the delimiter used in this " \
                           "file. Please use tab, comma, or semicolon."
                else:
                    raise e
            if dialect.delimiter not in ('\t', ',', ';'):
                return "Invalid delimiter detected. Please use tab, comma, " \
                       "or semicolon."
            csvfile.seek(0)
            r = csv.reader(csvfile, dialect)
            rowsSetup = False
            for row in r:
                if not rowsSetup:
                    self.setupRows(row)
                    rowsSetup = True
                else:
                    self.mkStudent(row)

        return self.errListFormat()

    def setupRows(self, headers):
        cols = {}
        for i in ('Device ID(s)', 'User ID', 'Last Name', 'First Name'):
            if i not in headers:
                raise ImporterError("A required header is missing! The file needs to contain the columns 'Device ID(s)', 'User ID', 'Last Name', and 'First Name' (and optionally 'Email'.")
        for i in headers:
            if not (i == 'Device ID(s)' or i == 'User ID' or i == 'Last Name' or
                    i == 'First Name' or i == 'Email'):
                self.errors.append((headers[0], "Warning: Unrecognized header %s. The import will ignore this column." % i))

        cols['tpdev'] = headers.index('Device ID(s)')
        cols['tpid'] = headers.index('User ID')
        cols['ln'] = headers.index('Last Name')
        cols['fn'] = headers.index('First Name')
        if 'Email' in headers:
            cols['email'] = headers.index('Email')
        else:
            cols['email'] = None
        self.cols = cols

    def mkStudent(self, row):
        cols = self.cols
        try:
            ln = row[cols['ln']]
            fn = row[cols['fn']]
            tpid = row[cols['tpid']]
            tpdev = row[cols['tpdev']]
            if cols['email'] is not None:
                email = row[cols['email']]
            else:
                email = ""
        except ValueError:
            self.errors.append((row[0], "Wrong number of columns for this row."))
            return
        except Exception as e:
            self.errors.append((row[0], e))
        else:
            if makesDupeStudent(ln, fn, tpid, tpdev, email, self.cls):
                self.errors.append((row[0], "Student already exists."))
                return
            elif ln == fn == tpid == tpdev == email == '':
                # blank line, but with delimiters; TP usually puts one at the
                # bottom when you export, so silently ignore
                return
            else:
                self.students.append(Student.createNew(
                        ln, fn, tpid, tpdev, email, self.cls))

    def errListFormat(self):
        """Provide user with a list of problems that occurred during import."""
        errString = ""
        num = 1
        for i in self.errors:
            errString += "\n\n#%i.\nStudent: %s\nError: %s" % (num, i[0], i[1])
            num += 1
        return errString.strip()

def importStudents(fname, cls):
    si = StudentImporter(fname, cls)
    errs = si.txtImport()
    return errs
