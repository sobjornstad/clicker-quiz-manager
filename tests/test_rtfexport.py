import unittest
import os
import sys
import filecmp
sys.path.append("../")

import db.database
import db.tools.create_database

from db.questions import Question
from db.rtfexport import *

TEST_DB_FNAME = "test.db"

class RtfExportTests(unittest.TestCase):
    def setUp(self):
        db.tools.create_database.makeDatabase(TEST_DB_FNAME)
        db.database.connect(TEST_DB_FNAME)

    def tearDown(self):
        db.database.connection.close()
        os.remove(TEST_DB_FNAME)

    def testRender(self):
        fname = 'testfile.rtf'
        against_fname = 'tests/resources/test_format_against.rtf'
        questions = [Question("Hello?", ["foo", "bar", "baz", "quux"], "c", 1, 1)]
        render(questions, fname)
        try:
            f = open(fname)
        except IOError:
            self.assertTrue(False), "File was not created successfully"
        else:
            self.assertTrue(f.readlines()), "No data in file"
            assert filecmp.cmp(fname, against_fname), \
                    "Output different from saved correct output file"
        finally:
            f.close()
            import os
            os.remove(fname)
