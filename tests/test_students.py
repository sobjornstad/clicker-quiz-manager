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

        assert s.csvRepr() == "Bjornstad\tSoren\t1\tc56a1\tcontact@sorenbjornstad.com", "%r" % s.csvRepr()

        assert len(studentsInClass(cls)) == 1 == len(studentsInClass(cls2))
        assert studentsInClass(cls)[0] == s
        assert studentsInClass(cls2)[0] == s2
