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

    def testBasicQuiz(self):
        cls = db.classes.Class("Test Class")
        st = db.sets.Set("Test Set", 1)
        q = db.questions.Question("What is the answer?",
                ["foo", "bar", "baz", "42"], "d", st, 1)
        st2 = db.sets.Set("Test Set", 1)
        q2 = db.questions.Question("What is the answer to this?",
                ["foo", "bar", "baz", "42"], "c", st2, 2)

        quiz = Quiz(cls)

        # configure
        quiz.addNewSet(st)
        quiz.addNewSet(st2)
        assert quiz.newSets == [st, st2]
        quiz.setNewQuestions(5)
        assert quiz.useNewNum == 5
        quiz.setRevQuestions(6)
        assert quiz.useRevNum == 6

        # fill new items
        quiz._fillNewItems()
        assert len(quiz.newQ) == 2

        # change the set2 one into a review item, move ourselves ahead a bit in
        # our review history, reload, and test new/rev load
        quiz.newQ[1].reschedule(3)
        d.cursor.execute('UPDATE classes SET setsUsed=? WHERE cid=?',
                (7,cls.getCid()))
        d.connection.commit()
        quiz.resetNewSets()
        quiz.addNewSet(st)
        quiz.finishSetup()
        assert len(quiz.newQ) == 1, quiz.newQ
        assert len(quiz.revQ) == 1, quiz.revQ

        # feedback from object itself on what's available
        assert quiz.getNewAvail() == 1
        assert quiz.getRevDue() == 1






if __name__ == "__main__":
    unittest.main()
