import utils
import db.database as d

import db.classes
import db.history
import db.questions
import db.sets
import db.students
from db.classes import Class
from db.sets import Set
from db.questions import Question
from db.genquiz import Quiz, SetRescheduler, getSetsUsed

class DbTests(utils.DbTestCase):
    def testDeletions(self):
        c = Class.createNew("Greta and TI 101")
        st = Set.createNew("Test Set", 3)
        q = Question("Hello?", ["foo", "bar", "baz", "quux"], "c", st, 1)
        q2 = Question("Goodbye?", ["1", "2", "3", "4"], "d", st, 2)

        # test question-set cascade
        assert db.questions.getById(q.getQid()) is not None
        assert db.questions.getById(q2.getQid()) is not None
        st.delete()
        assert db.questions.getById(q.getQid()) is None
        assert db.questions.getById(q2.getQid()) is None

        # test student-class cascade
        s = db.students.Student.createNew("Almzead", "Maud", "1", "ff8836",
                                          "maud@example.com", c)
        tpid = s.getTpid()
        assert db.students.findStudentByTpid(tpid, c) is not None
        db.classes.deleteClass(c.getName())
        assert db.students.findStudentByTpid(tpid, c) is None

        # test history/quiz-class cascade
        # (much code, with checks removed, from test_genquiz)
        def do():
            cls = db.classes.Class.createNew("Test Class")
            st = db.sets.Set.createNew("Test Set", 1)
            q = db.questions.Question("What is the answer?",
                    ["foo", "bar", "baz", "42"], "d", st, 1)
            q4 = db.questions.Question("What is the answer ?",
                    ["foo", "bar", "baz", "42"], "d", st, 4)
            st2 = db.sets.Set.createNew("Test Set", 1)
            q2 = db.questions.Question("What is the answer to this?",
                    ["foo", "bar", "baz", "42"], "c", st2, 2)
            q3 = db.questions.Question("What is the answer to this question?",
                    ["foo", "bar", "baz", "42"], "c", st2, 3)
            quiz = Quiz(cls)
            quiz.addNewSet(st)
            quiz.addNewSet(st2)
            quiz.setNewQuestions(1)
            quiz.setRevQuestions(2)
            quiz._fillNewItems()
            sr = SetRescheduler()
            quiz.newQ[0].reschedule(3, sr)
            quiz.newQ[1].reschedule(2, sr)
            sr.runResched()
            d.inter.exQuery('UPDATE classes SET setsUsed=? WHERE cid=?',
                    (7,cls.getCid()))
            d.inter.forceSave()
            quiz.resetNewSets()
            quiz.addNewSet(st2)
            quiz.finishSetup()
            quiz._randNew()
            quiz._randRev()
            qPrev = quiz.generate()
            oldSetsUsed = getSetsUsed(cls)
            quiz.rewriteSchedule()
            return cls, st
        # We now have a history entry and a quizzes entry.
        cls, st = do()
        quizHistoryItem = db.history.historyForClass(cls)[0]
        c = d.inter.exQuery('SELECT * FROM history WHERE sid=? AND cid=?',
                (st.getSid(), cls.getCid()))
        assert quizHistoryItem
        assert c.fetchall()
        db.classes.deleteClass(cls.getName())
        with self.assertRaises(IndexError):
            quizHistoryItem = db.history.historyForClass(cls)[0]
        c = d.inter.exQuery('SELECT * FROM history WHERE sid=? AND cid=?',
                (st.getSid(), cls.getCid()))
        assert not c.fetchall()
