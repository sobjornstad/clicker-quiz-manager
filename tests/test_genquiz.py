import db.questions
import db.sets
import db.classes
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

        # reschedule and check next set values
        item.reschedule(1)
        assert item.getNextSet() == 2, item.getNextSet()
        item.reschedule(3)
        assert item.getNextSet() == 6



if __name__ == "__main__":
    unittest.main()
