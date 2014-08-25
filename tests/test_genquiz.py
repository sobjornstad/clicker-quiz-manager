import db.questions
import db.sets
import db.classes
import db.database as d
from db.genquiz import *
import utils

class QuizTests(utils.DbTestCase):
    def testQuizItem(self):
        cls = db.classes.Class("Test Class")
        st = db.sets.Set("Test Set", 1)
        q = db.questions.Question("What is the answer?",
                ["foo", "bar", "baz", "42"], "d", st, 1)
        item = QuizItem(q, cls)

        # check default values
        assert item.getPriority() == (QuizItem.DEFAULT_PRIORITY / 1000)
        assert item.getLastSet() == 0
        assert item.getNextSet() == 0 # lastSet is 0

        # check private values
        assert item.qid == q.getQid()
        assert item.sid == q.getSid()
        assert item.ctype == 'new'

        # reschedule and check next set values
        item.reschedule(1)
        assert item.getNextSet() == 2, item.getNextSet()
        item.reschedule(3)
        assert item.getNextSet() == 6

        # pull in from db again and make sure it works
        itemRegrabbed = QuizItem(q, cls)
        assert item.ctype == 'rev'
        assert item.getNextSet() == 6
        assert item.qid == q.getQid()

    def testQuiz(self):
        cls = db.classes.Class("Test Class")
        st = db.sets.Set("Test Set", 1)
        q = db.questions.Question("What is the answer?",
                ["foo", "bar", "baz", "42"], "d", st, 1)
        q4 = db.questions.Question("What is the answer ?",
                ["foo", "bar", "baz", "42"], "d", st, 4)
        st2 = db.sets.Set("Test Set", 1)
        q2 = db.questions.Question("What is the answer to this?",
                ["foo", "bar", "baz", "42"], "c", st2, 2)
        q3 = db.questions.Question("What is the answer to this question?",
                ["foo", "bar", "baz", "42"], "c", st2, 3)

        quiz = Quiz(cls)

        # configure
        quiz.addNewSet(st)
        quiz.addNewSet(st2)
        assert quiz.newSets == [st, st2]
        quiz.setNewQuestions(1)
        assert quiz.useNewNum == 1
        quiz.setRevQuestions(2)
        assert quiz.useRevNum == 2
        assert not quiz.isSetUp()

        # fill new items
        quiz._fillNewItems()
        assert len(quiz.newQ) == 4

        # change the set1 ones into review items, move ourselves ahead a bit in
        # our review history, reload, and test new/rev load
        quiz.newQ[0].reschedule(3)
        quiz.newQ[1].reschedule(2)
        d.cursor.execute('UPDATE classes SET setsUsed=? WHERE cid=?',
                (7,cls.getCid()))
        d.connection.commit()
        quiz.resetNewSets()
        quiz.addNewSet(st2)
        quiz.finishSetup()
        assert quiz.isSetUp()
        assert len(quiz.newQ) == 2, quiz.newQ
        assert len(quiz.revQ) == 2, quiz.revQ

        # feedback from object itself on what's available
        assert quiz.getNewAvail() == 2
        assert quiz.getRevDue() == 2

        # fill with random questions
        quiz._randNew()
        quiz._randRev()
        assert len(quiz.newL) == 1, len(quiz.newL)
        assert quiz.newL[0].getQuestion() == q2 or \
                quiz.newL[0].getQuestion() == q3
        assert len(quiz.revL) == 2
        assert quiz.revL[0].getQuestion() == q or quiz.revL[0].getQuestion() == q4
        assert quiz.isSetUp(True)

        # generate
        qPrev = quiz.generate()
        quiz.makeRtfFile("tmp.rtf")
        from os import remove
        remove("tmp.rtf")
        # rendering is tested in test_rtfexport.py

        # reschedule
        oldSetsUsed = getSetsUsed(cls)
        quiz.rewriteSchedule()
        assert oldSetsUsed + 1 == getSetsUsed(cls)
        assert quiz.revL[1].getLastSet() == getSetsUsed(cls) -1

    def testFindSets(self):
        st1 = db.sets.Set("Test Set 1", 1)
        st2 = db.sets.Set("Test Set 2", 2)
        st3 = db.sets.Set("Test Set 3", 3)
        q1 = db.questions.Question("Q1", ['a', 'b', 'c'], 'a', st1, 1)
        q2 = db.questions.Question("Q2", ['a', 'b', 'c'], 'b', st2, 1)
        q3 = db.questions.Question("Q3", ['a', 'b', 'c'], 'c', st3, 1)
        cls = db.classes.Class("Test Class")

        # they should all be new and available -- there's nothing in history
        sts = findNewSets(cls)
        assert len(sts) == 3

        # fake some revs into the history table
        cid = cls.getCid()
        x = d.cursor.execute
        x('INSERT INTO history (cid, qid) VALUES (?,?)', (cid, st2.getSid()))
        x('INSERT INTO history (cid, qid) VALUES (?,?)', (cid, st3.getSid()))
        d.connection.commit()

        # now we should only have one new
        sts = findNewSets(cls)
        assert len(sts) == 1, len(sts)






if __name__ == "__main__":
    unittest.main()
