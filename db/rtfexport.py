# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2014 Soren Bjornstad. All rights reserved.

import PyRTF as rtf
import rtfunicode
from questions import Question

### OUTPUT TO FILE ###
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

def render(rtfObj, f):
    DR = rtf.Renderer()
    DR.Write(rtfObj, f)
