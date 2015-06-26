import filecmp

import utils
from db.questions import Question
from db.sets import Set
from db.output import *

class OutputTests(utils.DbTestCase):
    def testRTFRender(self):
        fname = 'testfile.rtf'
        against_fname = 'tests/resources/test_format_against.rtf'
        st = Set("Test Set", 2)
        questions = [Question("Hello?", ["foo", "bar", "baz", "quux"], "c", st, 1)]
        obj = genRtfFile(questions)
        render(obj, file(fname, 'wb'))
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

    def testLaTeXRender(self):
        # create some questions to render
        st = Set("Test Set", 1)
        q1 = Question("Hello?", ["foo", "bar", "baz", "quux"], "c", st, 1)
        q2 = Question("'Goodbye' is a [...].",
                ["word", "tar", "taz", "tuux"], "a", st, 1)
        q3 = Question("Auf wiedersehen? // Goodbye?",
                ["me", "you", "they", "I"], "b", st, 1)
        qs = [q1, q2, q3]

        # make sure that the rendered string is right
        latex = prepareLaTeXString(qs, DEFAULT_LATEX_HEADER, DEFAULT_LATEX_FOOTER)
        fname = 'testfile.tex'
        against_fname = 'tests/resources/test_latex_against.tex'

        # uncomment this and run test once to redo the against file:
        #with open(against_fname, 'wb') as f:
        #    f.write(latex)
        #return

        with open(fname, 'wb') as f:
            f.write(latex)
        try:
            f = open(fname)
        except IOError:
            assert False, "File was not created successfully"
        else:
            assert f.readlines(), "No data in LaTeX file"
            assert filecmp.cmp(fname, against_fname), \
                    "Output different from saved correct output file"
        finally:
            f.close()
            import os
            os.remove(fname)
