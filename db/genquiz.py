# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2014 Soren Bjornstad. All rights reserved.

import database as d
import questions
import output
import sets

import random

class SetRescheduler(object):
    def __init__(self):
        self.sts = {}

    def addSet(self, st, item):
        sid = st.getSid()
        if sid not in self.sts:
            self.sts[sid] = item

    def runResched(self):
        for st in self.sts:
            item = self.sts[st]
            #SAMPLE CODE FOLLOWS
            vals = {
                    'ns': item.nextSet,
                    'li': item.lastIvl,
                    'factor': item.factor,
                    'sid': item.sid,
                    'cid': item.cid
                   }

            if item.ctype == 'rev':
                d.cursor.execute('UPDATE history SET nextSet=:ns, factor=:factor, \
                                  lastIvl=:li WHERE sid=:sid AND cid=:cid', \
                                  vals)
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
    DEFAULT_FACTOR = 2000

    def __init__(self, q, cls):
        self.q = q
        qid = q.getQid()
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
        if self.lastIvl:
            self.lastIvl = (self.lastIvl * self.factor / 1000)
        else:
            self.lastIvl = 1

        self.nextSet = curSet + self.lastIvl
        sr.addSet(self.st, self)


class Quiz(object):
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

        Returns a plaintext preview string. Sets self.rtfObj to the RTF object
        to be output.
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


    def outputRoutine(func):
        def wrapper(self, *args, **kwargs):
            if not self.isSetUp() and rtfObj:
                assert False, "Need to call generate() first!"
            self.genQl = [i.getQuestion() for i in self.allQuestions]
            func(self, *args, **kwargs)
        return wrapper

    @outputRoutine
    def makeRtfFile(self, filename):
        """
        Write the generated questions out to an RTF file. Requires the filename,
        presumably obtained from the user via a file browse dialog.
        """
        rtfObj = output.genRtfFile(self.genQl)
        output.renderRTF(rtfObj, filename)

    @outputRoutine
    def makePdf(self, filename, className, quizNum):
        # at some point we might want to make provisions for passing other
        # makePaperQuiz options
        output.makePaperQuiz(self.genQl, className, quizNum,
                doOpen=False, doCopy=True, copyTo=filename)

    @outputRoutine
    def makeHtml(self, filename, cls, quizNum, forQuizzing=False):
        # ditto, on header paths
        content = output.htmlText(self.genQl, forQuizzing)
        output.renderHtml(content, cls, quizNum, filename)

    @outputRoutine
    def makeTxt(self, filename, cls, quizNum, forQuiz):
        content = output.genPlainText(self.genQl, forQuiz)
        output.renderTxt(content, cls, quizNum, filename)


    def rewriteSchedule(self):
        """
        Once the user has decided to use a set of cards, update cards' schedules
        to match the fact that they've been reviewed.
        """
        sr = SetRescheduler()
        curSet = getSetsUsed(self.cls)
        for i in (self.newL + self.revL):
            i.reschedule(curSet, sr)
        sr.runResched()
        incrementSetsUsed(self.cls)


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
            assert False, "Options not set up! This should be checked in caller!"
        self.newL = randomDraw(self.newQ, self.newSets, self.useNewNum)

    def _randRev(self):
        """
        Select review questions randomly from QuizItems that are due (in revQ),
        with the proviso that there must be at least one question from each set
        in the final draw.

        The result will be placed in self.revL. No return.
        """
        if not self.isSetUp():
            assert False, "Options not set up! This should be checked in caller!"

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
    cid = cls.getCid()
    d.cursor.execute('SELECT setsUsed FROM classes WHERE cid=?', (cid,))
    return d.cursor.fetchall()[0][0]
def incrementSetsUsed(cls):
    cid = cls.getCid()
    curVal = getSetsUsed(cls)
    d.cursor.execute('UPDATE classes SET setsUsed=? WHERE cid=?',
            (curVal+1, cid))
    d.checkAutosave()

def itemDue(item, curSet):
    """Determine if an item is currently due for review."""
    return True if (item.getNextSet() <= curSet) else False

def randomDraw(l, allSets, num):
    """
    Draw *num* QuizItems from *l*, requiring at least one from each set in
    *allSets*. Return a list of the drawing.
    """
    while True:
        if num > len(l):
            assert False, "More new questions requested than available!"
        L = random.sample(l, num)
        setsUsed = []
        for i in L:
            st = i.getQuestion().getSet()
            if st not in setsUsed:
                setsUsed.append(st)
        if setsUsed == allSets:
            break
        elif len(allSets) > num:
            # not enough room for all sets; would force infinite loop
            break

    return L

#         d.cursor.execute('''
#                    SELECT qid FROM history
#                    WHERE cid=:cid
#                    AND qid IN (SELECT qid FROM questions WHERE sid=:sid)''',
#                    {'cid': self.cls.getCid(), 'sid': i.getSid()})

