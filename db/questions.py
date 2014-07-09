# -*- coding: utf-8 -*-
import unittest

class QuestionFormatError(Exception):
    def __init__(self, emsg):
        self.emsg = emsg
    def __str__(self):
        return repr(self.emsg)

class Question(object):
    """
    Represents one stored multiple-choice question and its answers.

    A question has a question ID from the database (qid, TODO), question string
    (question), a list of answer strings (answersList), a correct answer string
    that is one of 'a' through 'e', and a set object (set, TODO).

    ##TODO: ^ The code should eventually be changed to match above schema
    """

    _qLetters = ['a', 'b', 'c', 'd', 'e']

    def __init__(self, question, answersList, correctAnswer):
        self.q = question
        self.a = answersList
        self.ca = correctAnswer
        self.prevalidate()

    def prevalidate(self):
        "Make sure provided question input is valid."
        # correct types
        if type(self.q) is not str or \
           type(self.a) is not list or \
           type(self.ca) is not str:
               raise QuestionFormatError("Program provided invalid question: " \
                       "wrong data type.")
        for ans in self.a:
            if type(ans) is not str:
                raise QuestionFormatError("Program provided invalid question:" \
                        " an answer choice was not a string.")

        # 3-5 answers
        if not 3 <= len(self.a) <= 5:
            raise QuestionFormatError("You must have 3-5 answers.")

        # correct answer must be a lc MC letter
        if self.ca not in self._qLetters:
            raise QuestionFormatError("The correct answer choice was not a " \
                    "valid letter.")

    def getFormattedContent(self, questionNum):
        "Return question data formatted for ExamView rtf file format."
        oQ = '.\t'.join([str(questionNum), self.q])
        curLetter = 0
        oA = []
        for ans in self.a:
            oA.append('.\t'.join([str(self._qLetters[curLetter]), ans]))
            curLetter += 1
        oCA = '\t'.join(['ANS:', self.ca])
        return oQ, oA, oCA