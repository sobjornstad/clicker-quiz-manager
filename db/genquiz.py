# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2014-2015 Soren Bjornstad. All rights reserved.

"""
Contains code for generating and scheduling quizzes. This module is somewhat
complicated and could probably use some refactoring.

Classes:
    SetRescheduler: Holds sets that are being put on a quiz for later
        scheduling.
    QuizItem: Holds a question and the code for scheduling it.
    Quiz: Holds the content needed for quizzes (in the form of QuizItems) and
        handles selecting questions and creating various output formats.

Functions:
    findNewSets: Return all sets that have not been used in a given class.
    getSetsUsed: Return all sets that *have* been used in a given class.
    incrementSetsUsed: Increment the setsUsed value for a class (a scheduling
        parameter).
    itemDue: Return True if a QuizItem is due for review now.
    randomDraw: Randomly choose QuizItems from a provided list.

Abbreviations used in this module:
    st: a Set
    sid: a set ID (primary key for sets)
    cid: a class ID (ditto for classes)
    hid: a history ID (ditto for history entries)
    q: the question text of a Question, or a query to send to SQL
    cls: a class (sorry, yes, this conflicts with the class method standard arg)
    ctype: whether a QuizItem is new or review
    ivl: interval (time between two reviews)
    sr: an instance of the SetRescheduler
    new/revL: a list of selected questions
    new/revQ: a list of all questions, selected or not
    rtfObj: instance of the RTF output's main class
    sn: the name of a set

Database schema for history table:
    hid: integer primary key for a history entry
    cid: foreign key for the class this entry belongs to
    sid: foreign key for the set this entry belongs to
    nextSet: the quiz number at which this set should next appear for review
    lastIvl: the number of quizzes that were added to nextSet at last
        scheduling time
    factor: the number by which lastIvl will be multiplied on schedule
"""

import datetime
import pickle
import random

import db.database as d
import db.questions as questions
import db.output as output
import db.sets as sets

class SetRescheduler(object):
    """
    A container for items that will need to be rescheduled once the quiz is
    generated.

    Public methods:
        addSet: add an item in a given set to the SetRescheduler's list
        runResched: run the reschedule for all items in the list
    """
    def __init__(self):
        self.sts = {}

    def addSet(self, st, item):
        """
        Add the given item to the SetRescheduler's data model. Duplicates are
        not added.
        """
        sid = st.getSid()
        if sid not in self.sts:
            self.sts[sid] = item

    def runResched(self):
        """
        Update the history table according to the scheduling information given
        by the QuizItem's rescheduling method.
        """
        for st in self.sts:
            item = self.sts[st]
            vals = {
                    'ns': item.nextSet,
                    'li': item.lastIvl,
                    'factor': item.factor,
                    'sid': item.sid,
                    'cid': item.cid
                   }

            if item.ctype == 'rev':
                d.cursor.execute('''UPDATE history
                                    SET nextSet=:ns, factor=:factor, lastIvl=:li
                                    WHERE sid=:sid AND cid=:cid''', vals)
            elif item.ctype == 'new':
                d.cursor.execute('INSERT INTO history \
                                 (cid, sid, nextSet, lastIvl, factor) \
                                 VALUES (:cid, :sid, :ns, :li, :factor)', vals)
                item.hid = d.cursor.lastrowid
                item.ctype = 'rev'
            else:
                assert False, "Invalid card type in QuizItem!"

        d.checkAutosave()


class QuizItem(object):
    """
    Handle rescheduling of one question. Stores the question, its set, and
    its scheduling information. Used as part of a Quiz.
    """

    DEFAULT_FACTOR = 2000

    def __init__(self, q, cls):
        self.q = q
        cid = cls.getCid()
        st = q.getSet()
        sid = st.getSid()

        d.cursor.execute('SELECT * FROM history WHERE sid=? AND cid=?',
                (sid, cid))
        try:
            self.hid, self.cid, self.sid, self.nextSet, self.lastIvl, \
                    self.factor = d.cursor.fetchall()[0]
        except IndexError:
            self.sid = sid
            self.cid = cid
            self.nextSet = 0
            self.lastIvl = 0
            self.factor = self.DEFAULT_FACTOR
            self.ctype = 'new'
        else:
            self.ctype = 'rev'

        self.st = sets.findSet(sid=self.sid)

    def getQuestion(self):
        return self.q
    def getNextSet(self):
        return self.nextSet

    def reschedule(self, curSet, sr):
        """
        Method for determining the quiz item's next interval.
        """
        if self.lastIvl:
            self.lastIvl = (self.lastIvl * self.factor / 1000)
        else:
            self.lastIvl = 1

        self.nextSet = curSet + self.lastIvl
        sr.addSet(self.st, self)


class Quiz(object):
    """
    Handles selecting questions for a quiz, rescheduling them, and outputting
    them to various formats.

    TODO: documentation of important methods
    """

    def __init__(self, classToUse):
        self.newSets = []
        self.newQ = [] # / for possible
        self.revQ = [] # \ questions
        self.newL = [] # / for selected
        self.revL = [] # \ questions
        self.cls = classToUse
        self.useNewNum = None
        self.useRevNum = None
        self.rtfObj = None
        self.allQuestions = None

    def addNewSet(self, st):
        if st not in self.newSets:
            self.newSets.append(st)
    def resetNewSets(self):
        self.newSets = []
    def getSetNames(self):
        """
        Get a comma-separated string of the sets that are currently available
        for post-generation display to the user, along with the number of sets
        that are represented by the string.
        """
        sns = [i.getName() for i in self.newSets]
        return (', '.join(sns)), len(sns)
    def getClass(self):
        return self.cls

    def setNewQuestions(self, num):
        self.useNewNum = num
    def setRevQuestions(self, num):
        self.useRevNum = num

    def finishSetup(self):
        """
        Fill the Quiz with possible questions, after choosing the sets we want.
        This can always be called again if desired.
        """
        self._fillNewItems()
        self._fillRevItems()

    def isSetUp(self, forGen=False):
        """
        Provides two different checks for confirming the object is properly set
        up. With forGen=True, makes sure random questions have been selected
        and the final set have been decided on. If False (default), confirms
        that we're *ready* to pull the random questions.
        """

        if not ((self.newQ or self.revQ) and self.useNewNum is not None
                and self.useRevNum is not None and self.newSets):
            return False
        if forGen and not (self.newL and self.revL):
            return False
        return True

    def getNewAvail(self):
        """
        Determine how many new questions are available for use. This will
        wrongly return 0 if we haven't run finishSetup() yet, so do that first.
        """
        if self.newQ:
            return len(self.newQ)
        else:
            return 0
    def getRevDue(self):
        "Same as getNewAvail for review cards."
        if self.revQ:
            return len(self.revQ)
        else:
            return 0

    def generate(self):
        """
        After everything has been set up, run to select final questions and
        output the results. Does *not* reschedule anything in case the user
        doesn't like the set that was chosen.

        It is the caller's responsibility to make sure that the quiz isSetUp.

        Returns a plaintext preview string.
        """

        # choose questions
        if not self.isSetUp():
            assert False, "Tried to generate quiz before setting it up!"
        self._randNew()
        self._randRev()

        # Run through questions, randomize order, and get content. Review and
        # new questions are mixed to promote better learning -- it has been
        # shown that people learn better when different types of questions are
        # mixed.
        self.allQuestions = self.newL + self.revL
        random.shuffle(self.allQuestions)

        ql = [i.getQuestion() for i in self.allQuestions]
        qPrev = output.genPlainText(ql)
        return qPrev

    def fetchQuestionsForOutput(self):
        """
        Retrieve the list of chosen questions so they can be output.
        """
        if not self.isSetUp() and rtfObj:
            assert False, "Need to call generate() first!"
        return [i.getQuestion() for i in self.allQuestions]

    def rewriteSchedule(self):
        """
        Once the user has decided to use a set of cards, update cards' schedules
        to match the fact that they've been reviewed.
        """
        sr = SetRescheduler()
        curSet = getSetsUsed(self.cls)
        for i in self.newL + self.revL:
            i.reschedule(curSet, sr)
        self.saveHistory()
        sr.runResched()
        incrementSetsUsed(self.cls)

    def saveHistory(self):
        """
        Save information about a quiz that's been generated to the database's
        history table for later reference. Called from self.rewriteSchedule().
        """
        cid = self.cls.getCid()
        qList = [i.getQuestion() for i in self.allQuestions]
        qPickle = pickle.dumps(qList)
        d.cursor.execute('SELECT MAX(seq) FROM quizzes WHERE cid=?', (cid,))
        lastSeq = d.cursor.fetchall()[0][0]
        seq = (lastSeq + 1) if lastSeq is not None else 1
        date = datetime.datetime.now().strftime('%Y-%m-%d')
        newQuestions = len(self.newL)
        revQuestions = len(self.revL)
        setNames = ', '.join([i.getName() for i in self.newSets])
        resultsFlag = 0 # clearly, there are no results imported yet
        notes = ''

        q = '''INSERT INTO quizzes
               (zid, cid, qPickle, newNum, revNum, newSetNames, seq,
                resultsFlag, datestamp, notes)
               VALUES (null, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        vals = (cid, qPickle, newQuestions, revQuestions, setNames, seq,
                resultsFlag, date, notes)
        d.cursor.execute(q, vals)
        d.checkAutosave()

    def _fillNewItems(self):
        """
        Fill the new question list with items of the appropriate sets (which
        have previously been added with addNewSet()). This does not do any
        checking to see if the set is actually new; the code using this class
        needs to figure out which sets are new (using the findNewSets()
        function in this module) and not allow others to be added as new sets.
        """

        self.newQ = [] # reset
        for st in self.newSets:
            ql = questions.getBySet(st)
            for q in ql:
                self.newQ.append(QuizItem(q, self.cls))

    def _fillRevItems(self):
        """
        Like _fillNewItems, but for review items.
        """
        # pull in all items that might be eligible based on their class
        cid = self.cls.getCid()
        d.cursor.execute('SELECT sid FROM history WHERE cid=?', (cid,))
        ql = []
        for st in d.cursor.fetchall():
            setQuestions = questions.getBySet(sets.findSet(sid=st[0]))
            for question in setQuestions:
                ql.append(QuizItem(question, self.cls))

        # reset the list, then add ones that are due
        self.revQ = []
        curSet = getSetsUsed(self.cls)
        for i in ql:
            if itemDue(i, curSet):
                self.revQ.append(i)

    def _randNew(self):
        """
        Select new questions randomly from the sets that have been added to the
        Quiz, with the proviso that there must be at least one question from
        each set in the final draw.

        The result will be placed in self.newL. No return.
        """

        if not self.isSetUp():
            assert False, \
                    "Options not set up! This should be checked in caller!"
        self.newL = randomDraw(self.newQ, self.newSets, self.useNewNum)

    def _randRev(self):
        """
        Select review questions randomly from QuizItems that are due (in revQ),
        with the proviso that there must be at least one question from each set
        in the final draw.

        The result will be placed in self.revL. No return.
        """
        if not self.isSetUp():
            assert False, \
                    "Options not set up! This should be checked in caller!"

        allRevSets = []
        for i in self.revQ:
            st = i.getQuestion().getSet()
            if st not in allRevSets:
                allRevSets.append(st)
        self.revL = randomDraw(self.revQ, allRevSets, self.useRevNum)

def findNewSets(cls):
    "Return a list of all sets that are *not* in review."
    cid = cls.getCid()
    d.cursor.execute('SELECT sid FROM history WHERE cid=?', (cid,))

    revs = [sets.findSet(sid=sid[0]) for sid in d.cursor.fetchall()]
    alls = sets.getAllSets()
    news = [i for i in alls if i not in revs]
    return news

def getSetsUsed(cls):
    """Return all sets that have been used in class /cls/."""
    cid = cls.getCid()
    d.cursor.execute('SELECT setsUsed FROM classes WHERE cid=?', (cid,))
    return d.cursor.fetchall()[0][0]

def incrementSetsUsed(cls):
    """
    Increment setsUsed value for class /cls/. setsUsed is used in conjunction
    with the history table's nextSet to determine when quizzes should appear
    again.
    """

    cid = cls.getCid()
    curVal = getSetsUsed(cls)
    d.cursor.execute('UPDATE classes SET setsUsed=? WHERE cid=?',
            (curVal+1, cid))
    d.checkAutosave()

def itemDue(item, curSet):
    """Determine if an item is currently due for review."""
    return True if (item.getNextSet() <= curSet) else False

def randomDraw(quizL, allSets, num):
    """
    Draw *num* QuizItems from *quizL*, requiring at least one from each set in
    *allSets*. Return a list of the drawing.
    """
    while True:
        if num > len(quizL):
            assert False, "More new questions requested than available!"
        chosen = random.sample(quizL, num)
        setsUsed = []
        for i in chosen:
            st = i.getQuestion().getSet()
            if st not in setsUsed:
                setsUsed.append(st)
        if setsUsed == allSets:
            break
        elif len(allSets) > num:
            # not enough room for all sets; would force infinite loop
            break

    return chosen
