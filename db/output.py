# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2014 Soren Bjornstad. All rights reserved.

import PyRTF as rtf
import rtfunicode
from questions import Question
import re

### RTF for TurningPoint ###
def getRTFFormattedContent(ques, questionNum):
    "Return question data formatted for ExamView rtf file format."

    oQ = '.\t'.join([str(questionNum), ques.getQuestion()])
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


def render(rtfObj, f):
    DR = rtf.Renderer()
    DR.Write(rtfObj, f)


### TEXT PREVIEW ###
# (Relies on the RTF functions above, as it's nearly the same format.)

def genPreview(questions):
    """Create a plaintext preview string of the rtf file."""
    prev = []
    qNum = 1
    for question in questions:
        q, a, ca = getRTFFormattedContent(question, qNum)
        st = question.getSet().getName()
        prev.append("%s (%s)" % (q, st))
        for ans in a:
            prev.append(ans)
        prev.append(ca + '\n')
        qNum += 1
    return '\n'.join(prev)


### LaTeX OUTPUT ###
DEFAULT_LATEX_HEADER = 'db/resources/latex_header_default.tex'
DEFAULT_LATEX_FOOTER = 'db/resources/latex_footer_default.tex'

def makePaperQuiz(questions, headerPath=DEFAULT_LATEX_HEADER,
        footerPath=DEFAULT_LATEX_FOOTER):
    latex = prepareLaTeXString(questions, headerPath, footerPath)

def munge_latex(s):
    "Escape characters reserved by LaTeX."

    # This escapes all special chars listed as catcodes in /The TeXbook/, p.37.
    # note that spacing is not guaranteed with things like the tilde and caret.
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

def prepareLaTeXString(questions, headerPath, footerPath):
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
    return header + '\n\n' + '\n\n'.join(text) + '\n\n' + footer
