# -*- coding: utf-8 -*-
import PyRTF as rtf

class Question(object):
    questionNum = 1
    _qLetters = ['a', 'b', 'c', 'd', 'e']
    
    def __init__(self, question, answersList, correctAnswer):
        self.q = question
        self.a = answersList
        self.ca = correctAnswer
        self.num = Question.questionNum
        Question.questionNum += 1
        self.prevalidate()

    def prevalidate(self):
        "Make sure provided question input is valid."
        # correct types
        if type(self.q) is not str or \
           type(self.a) is not list or \
           type(self.ca) is not str:
                assert(False)
        for ans in self.a:
            if type(ans) is not str:
                assert(False)

        # 3-5 answers
        if not 3 <= len(self.a) <= 5:
            assert(False)

        # correct answer must be a lc MC letter
        if self.ca not in self._qLetters:
            assert(False)

    def postvalidate(self, q, a, ca):
        "Internal self-check to make sure output being provided is valid."
        # question number
        if ".\t" not in q:
            assert(False)
        num = q.split('.')[0]
        try:
            num = int(num)
        except TypeError:
            assert(False)
        
        # answer letters
        for ans in a:
            if ".\t" not in ans:
                assert(False)
            let = ans.split('.\t')[0]
            if let not in self._qLetters:
                assert(False)

    def getFormattedContent(self):
        "Return question data formatted for ExamView rtf file format."
        oQ = '.\t'.join([str(self.num), self.q])
        curLetter = 0
        oA = []
        for ans in self.a:
            oA.append('.\t'.join([str(self._qLetters[curLetter]), ans]))
            curLetter += 1
        oCA = '\t'.join(['ANS:', self.ca])
        self.postvalidate(oQ, oA, oCA)
        return oQ, oA, oCA
    

def genRtfFile(questions):
    doc = rtf.Document()
    section = rtf.Section()
    doc.Sections.append(section)
    
    section.append("MULTIPLE CHOICE")
    section.append("") 
    for question in questions:
        q, a, ca = question.getFormattedContent()
        section.append(q)
        for ans in a:
            section.append(ans)
        section.append(ca)
        
    return doc

def OpenFile(name):
    return file(name, 'w')

if __name__ == '__main__':
    questions = []
    questions.append(
        Question("Hello?", ["foo", "bar", "baz", "quux"], "c"))
    questions.append(
        Question("Goodbye?", ["1", "2", "3", "4"], "d"))
    
    DR = rtf.Renderer()
    doc3 = genRtfFile(questions)
    DR.Write(doc3, OpenFile('newquestions.rtf'))
    print "Finished"
