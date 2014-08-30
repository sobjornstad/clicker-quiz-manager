# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2014 Soren Bjornstad. All rights reserved.


import json
import database as d
import sets

class QuestionFormatError(Exception):
    def __init__(self, emsg):
        self.emsg = emsg
    def __str__(self):
        return repr(self.emsg)

class DuplicateError(Exception):
    def __init__(self):
        pass
    def __str__(self):
        return "A question by that name already exists."

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
        if not qid:
            # if we already have the qid, it's in the db already
            if self.isDupe():
                raise DuplicateError
            if self.prevalidate():
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
    def setOrder(self, o, commit=True):
        self._order = o
        self.dump(commit)
    # not allowed: set change (TODO), qid change

    def dump(self, commit=True):
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
        if commit:
            d.connection.commit()

    def delete(self):
        """Delete a question from the db. Calling this alone may cause the
        database to end up in an inconsistent state with gaps in ord values,
        which are supposed to be adjacent, so always call delete through the
        question manager."""

        d.cursor.execute('DELETE FROM questions WHERE qid=?', (self._qid,))
        d.connection.commit()
        # we shouldn't use this instance again of course, but the class does
        # not enforce its nonuse.


    ### ERROR CHECKING ###
    def prevalidate(self):
        "Make sure provided question input is valid."
        # correct types
        if not isinstance(self._q, basestring) or \
           not isinstance(self._a, list) or \
           not isinstance(self._ca, basestring):
               raise QuestionFormatError("Program provided invalid question: " \
                       "wrong data type.")
               return False
        for ans in self._a:
            if not isinstance(ans, basestring):
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

    def isDupe(self):
        """Make sure provided question name isn't a duplicate of another
        question that already exists."""

        q = getByName(self._q)
        if q and (self._sid == q.getSid()):
            return True
        else:
            return False


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


class QuestionManager(object):
    """Stores a list of questions that are in a given set and searches through
    them as needed."""

    def __init__(self, set):
        self.set = set
        self.update()

    def update(self):
        """Update the list of questions from the db. Call this if questions
        have been changed outside of the QuestionManager instance."""

        self.q = getBySet(self.set)

    def __iter__(self):
        # you can iterate over the manager for a simple list of the questions
        for i in self.q:
            yield i

    def byId(self, qid):
        """Return a Question, given the qid. Return None if it doesn't
        exist."""

        for i in self.q:
            if i.getQid() == qid:
                return i
        return None

    def byOrd(self, ord):
        "Return a Question, given its ord. Return None if it doesn't exist."

        for i in self.q:
            if i.getOrder() == ord:
                return i
        return None

    def byName(self, name):
        """Return a Question, given its text. Return None if it doesn't
        exist."""

        for i in self.q:
            if i.getQuestion() == name:
                return i
        return None

    def rmQuestion(self, qu):
        "Remove a given (qu)estion from the manager and delete it from the db."

        st = qu.getSet()
        self.q.remove(qu)
        qu.delete()
        shiftOrds(st)
        self.update()


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

def getByName(name):
    #TODO: write a test for this function
    # and/or replace all 3 of these with a find() function like in sets.py
    """Return a Question, given its text. Return None if it doesn't exist."""

    d.cursor.execute('SELECT * FROM questions WHERE q=?', (name,))
    data = d.cursor.fetchall()
    if data:
        qid, order, q, ca, answers, sid = data[0]
        answers = json.loads(answers)
        return Question(q, answers, ca, sets.findSet(sid=sid), order, qid)
    else:
        return None

def getBySet(st):
    """Return a list of all questions in the given SET, sorted by their ORD."""
    sid = st.getSid()

    d.cursor.execute('SELECT * FROM questions WHERE sid = ? \
                      ORDER BY ord', (sid,))
    questionList = []
    for i in d.cursor.fetchall():
        qid, order, q, ca, answers, sid = i
        answers = json.loads(answers)
        questionList.append(Question(q, answers, ca, st, order, qid))

    return questionList

def swapRows(q1, q2):
    "Swap the ords of the two questions passed."
    r1, r2 = q1.getOrder(), q2.getOrder()
    q1.setOrder(r2, commit=False)
    q2.setOrder(r1, commit=False)
    d.connection.commit()

def shiftOrds(st):
    """Shift all ords in a given set to fill in a gap caused by deleting a
    question. You could call it the "ord defragmenter." """

    qs = getBySet(st) # ordered with lowest first
    curOrd = 0
    for q in qs:
        if q.getOrder() != curOrd:
            q.setOrder(curOrd, commit=False)
        curOrd += 1
    d.connection.commit()

def findNextOrd(st):
    """Find the next unused question ord in a set, or return 1 if there are
    no questions in the set yet."""
    sid = st.getSid()
    d.cursor.execute('SELECT MAX(ord) FROM questions WHERE sid = ?', (sid,))
    last = d.cursor.fetchall()[0][0]
    if last:
        return last + 1
    else:
        return 1
