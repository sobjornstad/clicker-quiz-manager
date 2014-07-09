import unittest
import os
import sys
sys.path.append("../")
import db.database
import db.tools.create_database

TEST_DB_FNAME = "test.db"

class DbTestCase(unittest.TestCase):
    # common to all database-using test cases
    def dbSetUp(self):
        db.tools.create_database.makeDatabase(TEST_DB_FNAME)
        db.database.connect(TEST_DB_FNAME)

    def dbTearDown(self):
        db.database.connection.close()
        os.remove(TEST_DB_FNAME)

    # reimplement these if additional setup is needed
    def setUp(self):
        self.dbSetUp()

    def tearDown(self):
        self.dbTearDown()
