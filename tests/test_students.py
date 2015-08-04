import os
import filecmp

import utils
from db.students import *
import db.classes

class StudentTests(utils.DbTestCase):
    def testClass(self):
        cls = db.classes.Class("MyClass")
        cls2 = db.classes.Class("MyOtherClass")
        s = Student.createNew("Bjornstadt", "Sorenn", "3", "c56al", "contact@sorenbjornstad.net", cls)
        s2 = Student.createNew("Almzead", "Maud", "2", "55655", "maud@sorenbjornstad.net", cls2)
        assert s.getLn() == "Bjornstadt"
        assert s.getFn() == "Sorenn"
        assert s.getTpid() == "3"
        assert s.getTpdev() == "c56al"
        assert s.getEmail() == "contact@sorenbjornstad.net"
        assert s.getClass() == cls, "%r | %r" % (s.getClass().getCid(), cls.getCid())
        # test set
        s.setLn("Bjornstad")
        assert s.getLn() == "Bjornstad"
        s.setFn("Soren")
        s.setTpid("1")
        s.setTpdev("c56a1")
        s.setEmail("contact@sorenbjornstad.com")

        # go through the db
        stid = s.getStid()
        sRefr = Student(stid)
        assert sRefr.getLn() == "Bjornstad"
        assert s.getFn() == "Soren"
        assert s.getTpid() == "1"
        assert s.getTpdev() == "c56a1"
        assert s.getEmail() == "contact@sorenbjornstad.com"
        assert s.getClass() == cls
        assert sRefr == s # should include above, but just in case...

        assert s.csvRepr() == "Bjornstad,Soren,1,c56a1,contact@sorenbjornstad.com", "%r" % s.csvRepr()

        assert len(studentsInClass(cls)) == 1 == len(studentsInClass(cls2))
        assert studentsInClass(cls)[0] == s
        assert studentsInClass(cls2)[0] == s2

    def testImporting(self):
        # simple valid file without emails, just like a default TP install's
        cls = db.classes.Class("TestClass (no pun intended)")
        fname = 'tests/resources/stuimport/valid-noemails.csv'
        errs = importStudents(fname, cls)
        assert not errs
        assert len(studentsInClass(cls)) == 3, len(studentsInClass(cls))
        assert studentsInClass(cls)[0].getLn() == "Bjornstad"
        assert studentsInClass(cls)[0].getEmail() == ""
        assert studentsInClass(cls)[0].getTpid() == "1"

        # as before, but with the addition of emails
        cls = db.classes.Class("TestClass2")
        fname = 'tests/resources/stuimport/valid-emails.csv'
        errs = importStudents(fname, cls)
        assert not errs
        assert len(studentsInClass(cls)) == 3, len(studentsInClass(cls))
        assert studentsInClass(cls)[0].getLn() == "Bjornstad"
        assert studentsInClass(cls)[0].getEmail() == "soren@example.com"
        assert studentsInClass(cls)[0].getTpid() == "1"

        # let's mix the order of the columns up a bit
        cls = db.classes.Class("TestClass3")
        fname = 'tests/resources/stuimport/mixed-cols-emails.csv'
        errs = importStudents(fname, cls)
        assert not errs
        assert len(studentsInClass(cls)) == 3, len(studentsInClass(cls))
        assert studentsInClass(cls)[0].getLn() == "Bjornstad"
        assert studentsInClass(cls)[0].getEmail() == "soren@example.com"
        assert studentsInClass(cls)[0].getTpid() == "1"

        # what about extraneous columns? they won't be imported of course, but
        # we should ignore those columns with a quiet warning.
        cls = db.classes.Class("TestClass4")
        fname = 'tests/resources/stuimport/valid-extracols.csv'
        errs = importStudents(fname, cls)
        assert errs
        assert "Unrecognized header" in errs and "FluxCapacitor" in errs
        assert len(studentsInClass(cls)) == 3, len(studentsInClass(cls))
        assert studentsInClass(cls)[0].getLn() == "Bjornstad"
        assert studentsInClass(cls)[0].getEmail() == "soren@example.com"
        assert studentsInClass(cls)[0].getTpid() == "1"

        # several invalid possibilities
        cls = db.classes.Class("TestClass5")
        fname = 'tests/resources/stuimport/invalid-wrongdelim.csv'
        errs = importStudents(fname, cls)
        assert errs, errs
        assert "Invalid delimiter" in errs
        assert len(studentsInClass(cls)) == 0, len(studentsInClass(cls))

        cls = db.classes.Class("TestClass6")
        fname = 'tests/resources/stuimport/invalid-dupe.csv'
        errs = importStudents(fname, cls)
        assert errs
        assert "Student already exists" in errs
        assert len(studentsInClass(cls)) == 3, len(studentsInClass(cls))

    def testExporting(self):
        cls = db.classes.Class("TestClass (no pun intended)")
        s = Student.createNew("Bjornstad", "Soren", "3", "c56al", "contact@sorenbjornstad.net", cls)
        s2 = Student.createNew("Almzead", "Maud,Her", "2", "55655", "maud@sorenbjornstad.net", cls)

        compare_against = 'tests/resources/test_stuexport.csv'
        floc = 'testStudents.csv'
        exportCsv(studentsInClass(cls), floc)
        assert filecmp.cmp(floc, compare_against), \
                "Output different from saved correct output file"
        os.remove(floc)
