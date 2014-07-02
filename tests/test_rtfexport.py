import unittest
import sys
sys.path.append("../")

from db.questions import Question
from db.rtfexport import *

class RtfExportTests(unittest.TestCase):
    def testRender(self):
        fname = 'testfile.rtf'
        questions = [Question("Hello?", ["foo", "bar", "baz", "quux"], "c")]
        render(questions, fname)
        try:
            f = open(fname)
        except IOError:
            self.assertTrue(False), "File was not created successfully"
        else:
            self.assertTrue(f.readlines()), "No data in file"
        finally:
            f.close()
            import os
            os.remove(fname)
