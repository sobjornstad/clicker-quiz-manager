import database as d
import questions
import sets

class QuizItem(object):
    DEFAULT_PRIORITY = 1000
    DEFAULT_FACTOR = 2000

    def __init__(self, q, cls):
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
        self.st = []
        pass

    def addNewSet(self, st):
        self.st.append(st)

    def setNewQuestions(self, num):
        pass
    def setRevQuestions(self, num):
        pass

    def getNewAvail(self):
        num = 1
        return num
    def getRevDue(self):
        num = 1
        return num

    def genQuiz(self):
        pass
        # return the string to save

    def rewriteSchedule(self):
        pass

    def _randNew(self, num):
        pass
    def _randRev(self, num):
        pass

    def _fillNewItems(self):
        pass
    def _fillRevItems(self):
        pass
