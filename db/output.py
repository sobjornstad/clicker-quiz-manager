# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2014 Soren Bjornstad. All rights reserved.

import os
import re
import tempfile
import shutil
import subprocess
import sys

import PyRTF as rtf
import rtfunicode

from questions import Question

OCCLUSION_OUTPUT = '_' * 8

### RTF for TurningPoint ###
def getRTFFormattedContent(ques, questionNum):
    "Return question data formatted for ExamView rtf file format."

    oQ = '.\t'.join([str(questionNum), ques.getQuestion()])
    oQ = oQ.replace('[...]', OCCLUSION_OUTPUT)
    curLetter = 0
    oA = []
    for ans in ques.getAnswersList():
        oA.append('.\t'.join([str(ques._qLetters[curLetter]), ans]))
        curLetter += 1
    oCA = '\t'.join(['ANS:', ques.getCorrectAnswer()])
    return oQ, oA, oCA

def genRtfFile(questions):
    doc = rtf.Document()
    section = rtf.Section()
    doc.Sections.append(section)

    section.append("MULTIPLE CHOICE")
    section.append("")
    qNum = 1
    for question in questions:
        q, a, ca = getRTFFormattedContent(question, qNum)

        q = q.encode('rtfunicode')
        q = q.replace('\\u9?', '\t')
        ca = ca.encode('rtfunicode')
        ca = ca.replace('\\u9?', '\t')

        section.append(q)
        for ans in a:
            ans = ans.encode('rtfunicode')
            ans = ans.replace('\\u9?', '\t')
            section.append(ans)
        section.append(ca)
        qNum += 1

    return doc


def renderRTF(rtfObj, fname):
    DR = rtf.Renderer()
    with open(fname, 'wb') as f:
        DR.Write(rtfObj, f)


### TEXT PREVIEW ###
def genPreview(questions):
    """Create a plaintext preview string of the rtf file."""
    indices = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4}
    letters = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e'}

    prev = []
    qNum = 1
    for question in questions:
        q = '. '.join([str(qNum), question.getQuestion()])
        q = q.replace('[...]', OCCLUSION_OUTPUT)
        a = question.getAnswersList()
        ca = question.getCorrectAnswer()
        st = question.getSet().getName()

        prev.append("%s (%s)" % (q, st))

        letterNum = 0
        for ans in a:
            prev.append("\t%s. %s" % (letters[letterNum], ans))
            letterNum += 1

        correctAnswerText = a[indices[question.getCorrectAnswer()]]
        ca = "Answer: (%s) %s" % (ca, correctAnswerText)
        prev.append(ca + '\n')
        qNum += 1
    return '\n'.join(prev)


### LaTeX OUTPUT ###
DEFAULT_LATEX_HEADER = 'db/resources/latex_header_default.tex'
DEFAULT_LATEX_FOOTER = 'db/resources/latex_footer_default.tex'

class LatexError(Exception):
    def __init__(self, emsg):
        self.emsg = emsg
    def __str__(self):
        return repr(self.emsg)
class UnopenableError(Exception):
    def __init__(self):
        self.emsg = "Could not open the file automatically."
    def __str__(self):
        return repr(self.emsg)

def autoOpen(path):
    """
    Open a given path with the system's automatic-filetype-detection program.
    """

    if sys.platform.startswith('linux'):
        subprocess.call(["xdg-open", path])
    elif sys.platform == "darwin":
        os.system("open %s" % path)
    elif sys.platform == "win32":
        os.startfile(path)
    else:
        raise UnopenableError


def makePaperQuiz(questions, cls, quiznum,
        headerPath=DEFAULT_LATEX_HEADER, footerPath=DEFAULT_LATEX_FOOTER,
        latexCommand='xelatex',
        doOpen=True, doCopy=False, copyTo=None):
    latex = prepareLaTeXString(questions, cls, quiznum, headerPath, footerPath)

    tdir = tempfile.mkdtemp()
    oldcwd = os.getcwd()
    os.chdir(tdir)

    fnamebase = "quiz"
    tfile = os.path.join(tdir, '.'.join([fnamebase, 'tex']))
    pdfFile = os.path.join(tdir, '.'.join([fnamebase, 'pdf']))
    with open(tfile, 'wb') as f:
        f.write(latex)
    try:
        subprocess.check_output([latexCommand, '-halt-on-error', tfile])
    except subprocess.CalledProcessError as e:
        raise LatexError("LaTeX Error %i:\n\n%s" % (e.returncode, e.output))
    except OSError as e:
        raise LatexError("LaTeX Error: unable to find LaTeX executable")
    else:
        if doOpen:
            autoOpen(pdfFile)
        if doCopy:
            assert copyTo is not None, "No destination location given!"
            shutil.copyfile(pdfFile, copyTo)
    finally:
        os.chdir(oldcwd)

    # ignore errors: it's not worth being a bother when we're just leaving a
    # temporary file lying around
    # TODO: COMMENTED OUT because it's deleting the file before the pdf viewer
    # gets to it! Ideally we would have some framework that could zap it when
    # the program closed. I think Anki handles this by having a global temp
    # folder for the whole program that can be accessed -- we could do this in
    # database.py.

    # shutil.rmtree(tdir, ignore_errors=True)


def munge_latex(s):
    "Escape characters reserved by LaTeX."

    # This escapes all special chars listed as catcodes in /The TeXbook/, p.37.
    # Note that spacing is not guaranteed with things like the tilde and caret.
    # However, those are not very likely to come up; we just don't want the
    # whole thing to crash if it does.
    s = s.replace('\\', '\\textbackslash ')
    s = s.replace('{', '\\{')
    s = s.replace('}', '\\}')
    s = s.replace('$', '\\$')
    s = s.replace('&', '\\&')
    s = s.replace('#', '\\#')
    s = s.replace('^', '\\textasciicircum ')
    s = s.replace('_', '\\textunderscore ')
    s = s.replace('~', '\\textasciitilde ')
    s = s.replace('%', '\\%')

    # Take care of straight quotation marks (single & double).
    # Note that it's not possible to handle single quotation marks correctly,
    # as there's no way to tell if it's an apostrophe or opening single quote.
    # If you want it right with singles, you need to use curlies in the question.
    s = re.sub('"(.*?)"', "``\\1''", s)

    return s

def prepareLaTeXString(questions, cls, quizNum, headerPath, footerPath):
    text = []
    qNum = 1
    for ques in questions:
        q = ques.getQuestion()
        quesIsMultiPart = False

        q = q.replace('[...]', '\\blank')
        qparts = q.split('//')
        if len(qparts) > 1:
            topline, botline = qparts
            topline, botline = topline.strip(), botline.strip()
            quesIsMultiPart = True

        # TODO: Handle using the \ten escape sequence here
        if quesIsMultiPart:
            txt = '\\doublequestion{%i}{%s}{%s}' % (qNum, topline, botline)
        else:
            txt = '\\singlequestion{%i}{%s}' % (qNum, q)

        text.append(txt)
        qNum += 1

    with open(headerPath) as f:
        header = f.read()
    with open(footerPath) as f:
        footer = f.read()

    header = header.replace('%%% INSERT CLASS HEADER HERE %%%',
            '\\header{%s}{%s}' % (cls, 'Quiz %i' % quizNum))
    return header + '\n\n' + '\n\n'.join(text) + '\n\n' + footer
