# -*- coding: utf-8 -*-
import json
import database as d
import sets

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
    that is one of 'a' through 'e', and a set object (st, TODO), and an order
    (order).

    ##TODO: ^ The code should eventually be changed to match above schema
    """

    _qLetters = ['a', 'b', 'c', 'd', 'e']

    def __init__(self, question, answersList, correctAnswer, st, order, qid=None):
        self._qid = qid
        self._q = question
        self._a = answersList
        self._ca = correctAnswer
        self._sid = st.getSid()
        self._order = order
        if (not qid) and self.prevalidate():
            # if we were passed qid, it must already be in the db as given
            self.dump()

    def __eq__(self, other):
        return (self._qid == other._qid and
                self._q == other._q and
                self._a == other._a and
                self._ca == other._ca and
                self._sid == other._sid and
                self._order == other._order)

    def __ne__(self, other):
        return not self.__eq__(other)


    ### GETTING ###
    def getQuestion(self):
        return self._q
    def getAnswersList(self):
        return self._a
    def getCorrectAnswer(self):
        return self._ca
    def getSid(self):
        return self._sid
    def getSet(self):
        return sets.findSet(sid=self._sid)
    def getOrder(self):
        return self._order
    def getQid(self):
        return self._qid

    ### SETTING AND MODIFYING ###
    def setQuestion(self, q):
        self._q = q
        self.dump()
    def setAnswersList(self, al):
        self._a = al
        self.dump()
    def setCorrectAnswer(self, ca):
        self._ca = ca
        self.dump()
    def setOrder(self, o):
        self._order = o
        self.dump()
    # not allowed: set change (TODO), qid change

    def dump(self):
        # 'new question'
        nq = {
              'question': self._q,
              'ca': self._ca,
              'answers': json.dumps(self._a),
              'order': self._order,
              'sid': self._sid
             }
        if self._qid:
            # exists already
            nq['qid'] = self._qid
            d.cursor.execute('UPDATE questions SET q=:question, ca=:ca, \
                    answers=:answers, ord=:order, sid=:sid WHERE qid=:qid', nq)

        else:
            d.cursor.execute('INSERT INTO questions \
                    (qid, ord, q, ca, answers, sid) VALUES \
                    (null, :order, :question, :ca, :answers, :sid)',
                    nq)
            self._qid = d.cursor.lastrowid

        # at some point we will want to eliminate this for performance reasons;
        # just leaving it here to make sure things are consistent for now
        d.connection.commit()


    ### ERROR CHECKING ###
    def prevalidate(self):
        "Make sure provided question input is valid."
        # correct types
        if type(self._q) is not str or \
           type(self._a) is not list or \
           type(self._ca) is not str:
               raise QuestionFormatError("Program provided invalid question: " \
                       "wrong data type.")
               return False
        for ans in self._a:
            if type(ans) is not str:
               raise QuestionFormatError("Program provided invalid question:" \
                       " an answer choice was not a string.")
               return False

        # 2-5 answers
        if not 2 <= len(self._a) <= 5:
            raise QuestionFormatError("You must have 2-5 answers.")
            return False

        # correct answer must be a lc MC letter
        if self._ca not in self._qLetters:
            raise QuestionFormatError("The correct answer choice was not a " \
                    "valid letter.")
            return False

        return True


    ### OUTPUT TO FILE ###
    def getFormattedContent(self, questionNum):
        """Return question data formatted for ExamView rtf file format. The
        number to place in front of the question is provided by caller, since
        this is determined at quiz generation time."""

        oQ = '.\t'.join([str(questionNum), self._q])
        curLetter = 0
        oA = []
        for ans in self._a:
            oA.append('.\t'.join([str(self._qLetters[curLetter]), ans]))
            curLetter += 1
        oCA = '\t'.join(['ANS:', self._ca])
        return oQ, oA, oCA



def getById(qid):
    """Return a Question from the db, given the qid. Return None if it doesn't
    exist."""

    d.cursor.execute('SELECT * FROM questions WHERE qid=?', (qid,))
    qid, order, q, ca, answers, sid = d.cursor.fetchall()[0]
    if qid:
        answers = json.loads(answers)
        return Question(q, answers, ca, sets.findSet(sid=sid), order, qid)
    else:
        return None
