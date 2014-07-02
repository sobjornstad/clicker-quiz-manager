import unittest
import sys
import filecmp
sys.path.append("../")

from db.questions import Question
from db.rtfexport import *

class RtfExportTests(unittest.TestCase):
    def testRender(self):
        fname = 'testfile.rtf'
        against_fname = 'resources/test_format_against.rtf'
        questions = [Question("Hello?", ["foo", "bar", "baz", "quux"], "c")]
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
