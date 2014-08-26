import database as d
import questions
import rtfexport
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
        return self.lastSet
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
        self.rtfObj = None

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
        allQuestions = self.newL + self.revQ
        random.shuffle(allQuestions)
        ql = [i.getQuestion() for i in allQuestions]

        qPrev = rtfexport.genPreview(ql)
        self.rtfObj = rtfexport.genRtfFile(ql)
        return qPrev

    def makeRtfFile(self, filename):
        """
        Write the generated questions out to an RTF file. Requires the filename,
        presumably obtained from the user via a file browse dialog.
        """
        if not self.isSetUp() and self.rtfObj:
            assert False, "Need to call generate() first!"
        with open(filename, 'wb') as f:
            rtfexport.render(self.rtfObj, f)

    def rewriteSchedule(self):
        """
        Once the user has decided to use a set of cards, update cards' schedules
        to match the fact that they've been reviewed.
        """
        curSet = getSetsUsed(self.cls)
        for i in (self.newL + self.revL):
            i.reschedule(curSet)
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
        d.cursor.execute('SELECT qid FROM history WHERE cid=?', (cid,))
        ql = [QuizItem(questions.getById(i[0]), self.cls)
              for i in d.cursor.fetchall()]

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
def incrementSetsUsed(cls):
    cid = cls.getCid()
    curVal = getSetsUsed(cls)
    d.cursor.execute('UPDATE classes SET setsUsed=? WHERE cid=?',
            (curVal+1, cid))
    d.connection.commit()

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

