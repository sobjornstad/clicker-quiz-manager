import utils
import db.classes
import time
import db.database as database

class DbTests(utils.DbTestCase):
    def testDbAutosave(self):
        # create a class as a test db item
        c1 = db.classes.Class("Greta and IT 101")
        assert c1.getCid() is not None, "cid unset after dump"

        database.forceSave()
        assert database.checkAutosave() == False # 60 seconds have not passed yet

        c2 = db.classes.Class("Greta and IT 353")
        time.sleep(0.05)
        assert database.checkAutosave(10) == False
        assert database.checkAutosave(0.04) == True # also activates save
        assert database.checkAutosave() == False
        assert db.classes.getClassByName("Greta and IT 353")



#        # change the name; check for same cid and new name
#        savedCid = c.getCid()
#        c.setName("Greta and IT 101")
#        assert savedCid == c.getCid(), "cid changed after update"
#        assert c.getName() == "Greta and IT 101"
#
#        # pull the class back in and make sure it's the same
#        c2 = db.classes.getClassByCid(c.getCid())
#        assert c2 is not None, "class did not exist in db"
#        assert c == c2, "newly pulled class not identical to orig"
#
#        # delete the class
#        db.classes.deleteClass(c2.getName())
#        cid = c2.getCid()
#        #assertRaises(
#
