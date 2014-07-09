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
        os.remove(TEST_DB_FNAME)

    def testDbWriteRead(self):
        # create a set in db; make sure it has a sid
        s = db.sets.Set("Maud's Questions", 3)
        s.dump()
        assert s.sid is not None, "sid unset after dump"

        # update the set; sid should not change
        savedSid = s.sid
        s.name = "Maud's Question Set"
        s.dump()
        assert savedSid == s.sid, "sid changed after update"

        # pull the set back in and make sure it's the same
        s2 = db.sets.setBySid(s.sid)
        assert s2 is not None, "sid did not exist in db"
        assert s.name == s2.name, "%r %r" % (s.name, s2.name)
        assert s.num == s2.num
