import utils
from db.students import *

class StudentTests(utils.DbTestCase):
    def testClass(self):
        s = Student.createNew("Bjornstadt", "Sorenn", "3", "c56al", "contact@sorenbjornstad.net")
        assert s.getLn() == "Bjornstadt"
        assert s.getFn() == "Sorenn"
        assert s.getTpid() == "3"
        assert s.getTpdev() == "c56al"
        assert s.getEmail() == "contact@sorenbjornstad.net"
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
        assert sRefr == s # should include above, but just in case...

        assert s.csvRepr() == "Bjornstad\tSoren\t1\tc56a1\tcontact@sorenbjornstad.com", "%r" % s.csvRepr()
