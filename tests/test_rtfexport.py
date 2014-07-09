import filecmp

import utils
from db.questions import Question
from db.rtfexport import *

class RtfExportTests(utils.DbTestCase):
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
