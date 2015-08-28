import os
import time
import utils
import db.classes
import db.database as d

class DbTests(utils.DbTestCase):
    def testDbAutosave(self):
        # create a class as a test db item
        c1 = db.classes.Class.createNew("Greta and IT 101")
        assert c1.getCid() is not None, "cid unset after dump"

        d.inter.forceSave()
        assert d.inter.checkAutosave() == False # 60 seconds have not passed yet

        c2 = db.classes.Class.createNew("Greta and IT 353")
        time.sleep(0.05)
        assert d.inter.checkAutosave(10) == False
        assert d.inter.checkAutosave(0.04) == True # also activates save
        assert d.inter.checkAutosave() == False
        assert db.classes.getClassByName("Greta and IT 353")


class DbTestsOnDisk(utils.DbTestCase):
    dbname = 'tempdb.db'

    def dbSetUp(self):
        # reimplemented
        try:
            os.remove(self.dbname)
        except OSError:
            pass
        db.tools.create_database.makeDatabase(self.dbname)
        conn = d.DatabaseInterface.connectToFile(self.dbname)
    def dbTearDown(self):
        d.inter.close()
        os.remove(self.dbname)

    def testDbOnDisk(self):
        # test the auxiliary connection option (for use with threads).

        # create a class as a test db item
        c1 = db.classes.Class.createNew("Greta and IT 101")
        d.inter.forceSave()

        #auxConn = database.takeOutNewConnection()
        #auxConn.cursor().execute('''INSERT INTO classes (cid, name, setsUsed)
        #                            VALUES (null, "Maud 101", 0)''')
        #auxConn.commit()

        #assert db.classes.getClassByName("Maud 101") is not None


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
