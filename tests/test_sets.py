import unittest
import os
import sys
sys.path.append("../")

import db.sets
import db.database
import db.tools.create_database

TEST_DB_FNAME = "test.db"


class SetTests(unittest.TestCase):
    def setUp(self):
        db.tools.create_database.makeDatabase(TEST_DB_FNAME)
        db.database.connect(TEST_DB_FNAME)

    def tearDown(self):
        db.database.connection.close()
        os.remove(TEST_DB_FNAME)

    def testDbWriteRead(self):
        # create a set in db; make sure it has a sid
        s = db.sets.Set("Maud's Questions", 3)
        assert s.getSid() is not None, "sid unset after dump"

        # update the set; sid should not change
        savedSid = s.getSid()
        s.setName("Maud's Question Set")
        s.dump()
        assert savedSid == s.getSid(), "sid changed after update"

        # pull the set back in and make sure it's the same
        s2 = db.sets.getSetBySid(s.getSid())
        assert s2 is not None, "set did not exist in db"
        assert s.getName() == s2.getName()
        assert s.getNum()== s2.getNum()
