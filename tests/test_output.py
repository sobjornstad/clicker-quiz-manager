# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2015 Soren Bjornstad. All rights reserved.

import filecmp
import os

from nose.plugins.attrib import attr

import utils
from db.questions import Question
from db.sets import Set
from db.output import *
from db.output import _htmlText
from db.classes import Class

class OutputTests(utils.DbTestCase):
    def testRTFRender(self):
        fname = 'testfile.rtf'
        against_fname = 'tests/resources/test_format_against.rtf'
        st = Set.createNew("Test Set", 2)
        questions = [Question("Hello [...]?", ["foo", "bar", "baz", "quux"],
            "c", st, 1)]
        renderRTF(questions, fname)
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
            os.remove(fname)

    def testPreviewRender(self):
        checkstr = """
1. Hello? (Test Set)
	a. foo
	b. bar
	c. baz
	d. quux
Answer: (c) baz

2. 'Goodbye' is a ________. (Test Set)
	a. word
	b. tar
	c. taz
	d. tuux
Answer: (a) word

3. Auf wiedersehen? // Goodbye? (Test Set)
	a. me
	b. you
	c. they
	d. I
Answer: (b) you
""".strip()

        qs = makeTestQuestions()
        txt = genPlainText(qs).strip()
        assert txt == checkstr

    def testLaTeXRender(self):
        qs = makeTestQuestions()
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
            os.remove(fname)

    def testLaTeXMunge(self):
        badstr = r"""
This {is} some text, which costs $4 & 50 cents, which is #1 in annoyance for people trying to use \ write it in LaTeX who don't ‘know’ much ~ it. That's because it's 100% "impossible" to parse unless “you” do_it_correctly, paying attention to ^ everything.
""".strip()

        checkstr = r"""
This \{is\} some text, which costs \$4 \& 50 cents, which is \#1 in annoyance for people trying to use \textbackslash  write it in LaTeX who don't ‘know’ much \textasciitilde  it. That's because it's 100\% ``impossible'' to parse unless “you” do\textunderscore it\textunderscore correctly, paying attention to \textasciicircum  everything.
""".strip()

        goodstr = munge_latex(badstr)
        assert goodstr == checkstr

        #with open ('/home/soren/output', 'wb') as f:
        #    f.write(goodstr)

    @attr('slow')
    def testLaTeXRender(self):
        qs = makeTestQuestions()
        cls = Class.createNew("German 101")
        quizNum = 1
        renderPdf(qs, cls, quizNum, doOpen=False)
        with self.assertRaises(LatexError) as ex:
            renderPdf(qs, cls, quizNum,
                    latexCommand='flibbertygibbertyaoeu', doOpen=False)
        with self.assertRaises(LatexError) as ex:
            renderPdf(qs, cls, quizNum, doOpen=False,
                    headerPath='tests/resources/latex_header_invalid.tex')


    def testHTMLRender(self):
        qs = makeTestQuestions()

        with open('tests/resources/test_html_export_forquizzing.html') as f:
            txt = f.read()
        assert txt.strip() == _htmlText(qs, forQuiz=True).strip()

        with open('tests/resources/test_html_export_notforquizzing.html') as f:
            txt2 = f.read()
        assert txt2.strip() == _htmlText(qs, forQuiz=False).strip()

        cls = Class.createNew("German 101")
        quizNum = 1
        fname = "test_htmlrender"
        against_fname = "tests/resources/test_html_complete.html"

        try:
            renderHtml(qs, cls, quizNum, fname, forQuiz=False)
            assert filecmp.cmp(fname, against_fname), \
                    "Output different from saved correct output file"
        finally:
            os.remove(fname)




def makeTestQuestions():
    # create some questions to render
    st = Set.createNew("Test Set", 1)
    q1 = Question("Hello?", ["foo", "bar", "baz", "quux"], "c", st, 1)
    q2 = Question("'Goodbye' is a [...].",
            ["word", "tar", "taz", "tuux"], "a", st, 1)
    q3 = Question("Auf wiedersehen? // Goodbye?",
            ["me", "you", "they", "I"], "b", st, 1)
    qs = [q1, q2, q3]
    return qs
