import unittest

import db.database
import db.tools.create_database

# use a test db in memory, which is waaaaaaay faster
TEST_DB_FNAME = ":memory:"

class DbTestCase(unittest.TestCase):
    # common to all database-using test cases
    def dbSetUp(self):
        conn = db.tools.create_database.makeDatabase(TEST_DB_FNAME)
        db.database.DatabaseInterface(conn)

    def dbTearDown(self):
        db.database.inter.close()

    # reimplement these if additional setup is needed
    def setUp(self):
        self.dbSetUp()

    def tearDown(self):
        self.dbTearDown()
