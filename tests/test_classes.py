import utils
import db.classes

class ClassTests(utils.DbTestCase):
    def testDbWriteRead(self):
        # create a class
        c = db.classes.Class("Greta and TI 101")
        assert c.getCid() is not None, "cid unset after dump"

        # change the name; check for same cid
        savedCid = c.getCid()
        c.setName("Greta and IT 101")
        assert savedCid == c.getCid(), "cid changed after update"

        # pull the class back in and make sure it's the same
        c2 = db.classes.getClassByCid(c.getCid())
        assert c2 is not None, "class did not exist in db"
        assert c == c2, "newly pulled class not identical to orig"

    def testGets(self):
        # create two classes
        c = db.classes.Class("First Class")
        c2 = db.classes.Class("Second Class")

        # pull list of classes and make sure it contains what we added
        cl = db.classes.getAllClasses()
        assert len(cl) == 2, cl
        assert cl[0] == c and cl[1] == c2

        # get class 2 by name
        cByName = db.classes.getClassByName("Second Class")
        assert cByName == c2

