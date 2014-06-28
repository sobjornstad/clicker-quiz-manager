import unittest, nose
import sys
sys.path.append("../")

from db.questions import *

class QuestionTests(unittest.TestCase):
    def setUp(self):
        self.questions = []
        self.questions.append(
            Question("Hello?", ["foo", "bar", "baz", "quux"], "c"))
        self.questions.append(
            Question("Goodbye?", ["1", "2", "3", "4"], "d"))

    def testAnswerOutput(self):
        q, a, ca = self.questions[0].getFormattedContent()
        for ans in a:
            self.failUnless(".\t" in ans)
            let = ans.split('.\t')[0]
            self.assertTrue(let in Question._qLetters), \
                    "Answer letter missing or incorrect on answer %r" % ans

    def testCorrectAnswerOutput(self):
        q, a, ca = self.questions[0].getFormattedContent()

        self.assertTrue('\t' in ca), "Missing tab"
        ans, let = ca.split('\t')
        self.assertTrue(ans == 'ANS:')
        self.assertTrue(let in Question._qLetters)

    def testQNumOutput(self):
        q, a, ca = self.questions[0].getFormattedContent()

        self.assertTrue(".\t" in q), "Missing tab"
        num = q.split('.')[0]
        try:
            num = int(num)
        except TypeError:
            self.assertTrue(False), "Returned question number not an int"

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

if __name__ == "__main__":
    unittest.main()
