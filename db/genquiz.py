import database as d
import questions
import sets

import random

#TODO: Factor needs to become an attribute of a *set* somehow (this might even need another *table* to fix). For now it's okay since we don't intend to change it. This needs to be done because otherwise some questions of a set might end up eligible while others don't.

class QuizItem(object):
    DEFAULT_PRIORITY = 1000
    DEFAULT_FACTOR = 2000

    def __init__(self, q, cls):
        self.q = q
        qid = q.getQid()
        cid = cls.getCid()

        d.cursor.execute('SELECT * FROM history WHERE qid=? AND cid=?',
                (qid, cid))
        try:
            self.hid, self.cid, self.qid, self.lastSet, self.factor, \
                    self.priority = d.cursor.fetchall()[0]
        except IndexError:
            self.qid = qid
            self.cid = cid
            self.lastSet = 0
            self.factor = self.DEFAULT_FACTOR
            self.priority = self.DEFAULT_PRIORITY
            self.ctype = 'new'
        else:
            self.ctype = 'rev'

        d.cursor.execute('SELECT sid FROM questions WHERE qid=?', (qid,))
        self.sid = d.cursor.fetchall()[0][0]

    def _dump(self):
        """Writes rescheduled values to the database."""
        vals = {
                'ls': self.lastSet,
                'factor': self.factor,
                'prior': self.priority,
                'qid': self.qid,
                'cid': self.cid
               }

        if self.ctype == 'rev':
            d.cursor.execute('UPDATE history SET lastSet=:ls, factor=:factor, \
                              priority=:prior WHERE qid=:qid AND cid=:cid', \
                              vals)
        elif self.ctype == 'new':
            d.cursor.execute('INSERT INTO history \
                             (cid, qid, lastSet, factor, priority) \
                             VALUES (:cid, :qid, :ls, :factor, :prior)', vals)
            self.hid = d.cursor.lastrowid
            self.ctype = 'rev'
        else:
            assert False, "Invalid card type in QuizItem!"
        d.connection.commit()

    def getQuestion(self):
        return self.q
    def getLastSet(self):
        return self.lastSet / 1000
    def getNextSet(self):
        return (self.lastSet * self.factor / 1000)
    def getPriority(self):
        return self.priority / 1000

    def reschedule(self, curSet):
        self.lastSet = curSet
        # consider decreasing the priority here; since we've seen the question
        # once, better to give other questions from the set a shot?
        self._dump()


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

    def addNewSet(self, st):
        if st not in self.newSets:
            self.newSets.append(st)
    def resetNewSets(self):
        self.newSets = []

    def setNewQuestions(self, num):
        self.useNewNum = num
    def setRevQuestions(self, num):
        self.useRevNum = num

    def finishSetup(self):
        """
        Fill the Quiz with possible questions, after choosing the sets and
        number of questions we want. This can always be called again if
        desired.
        """
        self._fillNewItems()
        self._fillRevItems()

    def isSetUp(self, forGen=True):
        """
        Provides two different checks for confirming the object is properly set
        up. With forGen=True (default), makes sure random questions have been
        selected and the final set have been decided on. If False, confirms that
        we're *ready* to pull the random questions.
        """

        if not (self.newQ and self.revQ and self.useNewNum and self.useRevNum
                and self.newSets):
            return False
        if forGen and not (self.newL and self.revL):
            return False
        return True

    def getNewAvail(self):
        """
        Determine how many new questions are available for use, or None if we
        haven't decided on our settings yet.
        """
        if self.newQ:
            return len(self.newQ)
        else:
            return None
    def getRevDue(self):
        "Same as getNewAvail for review cards."
        if self.revQ:
            return len(self.revQ)
        else:
            return None

    def genQuiz(self):
        pass
        # return the string to save

    def rewriteSchedule(self):
        pass

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
        d.cursor.execute('SELECT qid FROM history WHERE cid=?', (cid,))
        ql = [QuizItem(questions.getById(i[0]), self.cls)
              for i in d.cursor.fetchall()]

        # reset the list, then add ones that are due
        self.revQ = []
        curSet = getSetsUsed(self.cls)
        for i in ql:
            if itemDue(i, curSet):
                self.revQ.append(i)

    def _randNew(self, num):
        """
        Select new questions randomly from the sets that have been added to the
        Quiz, with the proviso that there must be at least one question from
        each set in the final draw.

        The result will be placed in self.newL. No return.
        """

        if not self.isSetUp(False):
            assert False, "Options not set up! This should be checked in caller!"
        self.newL = randomDraw(self.newQ, self.newSets, self.useNewNum)

    def _randRev(self, num):
        """
        Select review questions randomly from QuizItems that are due (in revQ),
        with the proviso that there must be at least one question from each set
        in the final draw.

        The result will be placed in self.revL. No return.
        """
        if not self.isSetUp(False):
            assert False, "Options not set up! This should be checked in caller!"

        allRevSets = [i.getQuestion().getSet() for i in self.revQ]
        self.revL = randomDraw(self.revQ, allRevSets, self.useRevNum)

def findNewSets(cls):
    "Return a list of all sets that are *not* in review."
    cid = cls.getCid()
    d.cursor.execute('''SELECT sid FROM questions
                        WHERE qid in (SELECT qid FROM history
                                      WHERE cid=?)''', (cid,))

    revs = [sets.findSet(sid=sid[0]) for sid in d.cursor.fetchall()]
    alls = sets.getAllSets()
    news = [i for i in alls if i not in revs]
    return news

def getSetsUsed(cls):
    cid = cls.getCid()
    d.cursor.execute('SELECT setsUsed FROM classes WHERE cid=?', (cid,))
    return d.cursor.fetchall()[0][0]

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
        sts = [i.getQuestion().getSet() for i in l]
        intersect = [i for i in sts if i in allSets]
        if intersect == sts:
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
