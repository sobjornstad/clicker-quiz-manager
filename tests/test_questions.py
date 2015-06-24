from db.questions import *
from db.sets import Set
import utils

class QuestionTests(utils.DbTestCase):
    def testGettersSetters(self):
        # compile a sample question
        q = "What is Maud's family name?"
        a = ["Bethamer", "Thorne", "Almzead", "Jallwei"]
        ca = "c"
        order = 1
        st = Set("Maudiverse Set", 5)
        ques = Question(q, a, ca, st, order)

        # make sure getters work
        assert ques.getQuestion() == q
        assert ques.getAnswersList() == a
        assert ques.getCorrectAnswer() == ca
        assert ques.getSid() == st.getSid()
        assert ques.getSet().getSid() == st.getSid()
        assert ques.getOrder() == order
        assert ques.getQid()

        # try editing
        nq = "Which of these names belonged to Maud's mother?"
        ques.setQuestion(nq)
        na = ["Bethamer", "Thorne", "Ohlo", "Almzead"]
        ques.setAnswersList(na)
        nca = 'd'
        ques.setCorrectAnswer(nca)
        norder = 2
        ques.setOrder(norder)

        # make sure values were updated
        assert ques.getQuestion() == nq
        assert ques.getAnswersList() == na
        assert ques.getCorrectAnswer() == nca
        assert ques.getOrder() == norder

    def testDbWriteRead(self):
        # create a question
        st = Set("Test Set", 3)
        q = Question("Hello?", ["foo", "bar", "baz", "quux"], "c", st, 1)
        qid = q.getQid()

        # read back in, make sure they're the same
        q2 = getById(qid)
        assert q == q2

    def testOutput(self):
        st = Set("Test Set", 3)
        q = Question("Hello?", ["foo", "bar", "baz", "quux"], "c", st, 1)
        q2 = Question("Goodbye?", ["1", "2", "3", "4"], "d", st, 2)
        questions = [q, q2]

        # answers
        q, a, ca = questions[0].getFormattedContent(1)
        for ans in a:
            self.failUnless(".\t" in ans)
            let = ans.split('.\t')[0]
            self.assertTrue(let in Question._qLetters), \
                    "Answer letter missing or incorrect on answer %r" % ans

        # correct answer
        q, a, ca = questions[0].getFormattedContent(2)

        self.assertTrue('\t' in ca), "Missing tab"
        ans, let = ca.split('\t')
        self.assertTrue(ans == 'ANS:')
        self.assertTrue(let in Question._qLetters)

        # question number
        q, a, ca = questions[0].getFormattedContent(3)

        self.assertTrue(".\t" in q), "Missing tab"
        num = q.split('.')[0]
        try:
            num = int(num)
        except TypeError:
            self.assertTrue(False), "Returned question number not an int"

    def testSetGet(self):
        st = Set("Test Set", 4)
        # these are in the set
        q = Question("Hello?", ["foo", "bar", "baz", "quux"], "c", st, 1)
        q2 = Question("Goodbye?", ["1", "2", "3", "4"], "d", st, 2)
        # this is *not* (included to be sure it doesn't accidentally get pulled)
        q3 = Question("Bye-bye?", ["1", "2", "3", "4"], "d", Set("t", 2), 2)

        # make sure gotten questions and originals are the same
        sets = getBySet(st)
        assert len(sets) == 2
        assert sets[0].getQid() == q.getQid()
        assert sets[1].getQid() == q2.getQid()

    def testDupeQuestionNames(self):
        st = Set("Test Set", 1)
        st2 = Set("Test Set 2", 2)
        q = Question("What is the answer?", ["foo", "bar", "baz", "42"],
                "d", st, 1)
        with self.assertRaises(DuplicateError):
            Question("What is the answer?", ["foo", "bar", "42", "quux"],
                    "c", st, 2)
        try:
            # this one should be fine
            Question("What is the answer to another question?",
                    ["foo", "bar", "42", "quux"], "c", st, 2)
            # and this one tests whether it correctly doesn't consider things
            # in different sets as dupes when they otherwise are
            Question("What is the answer?",
                    ["foo", "bar", "42", "quux"], "c", st2, 3)
        except Exception as e:
            assert False, e

    def testQuestionManager(self):
        st = Set("Test Set", 1)
        q1 = Question("What is the answer?",
                ["foo", "bar", "baz", "42"], "d", st, 1)
        q2 = Question("What is the answer to this one?",
                ["foo", "bar", "42", "quux"], "c", st, 2)
        qm = QuestionManager(st)

        # iter
        qs_from_qm = [i for i in qm]
        assert len(qs_from_qm) == 2
        assert qs_from_qm[0] == q1
        assert qs_from_qm[1] == q2

        # byId
        qid = q1.getQid()
        qbyid = qm.byId(qid)
        assert qbyid == q1

        # byName
        qname = q1.getQuestion()
        qbyname = qm.byName(qname)
        assert qbyname == q1

        # byOrd
        qord = q1.getOrder()
        qbyord = qm.byOrd(qord)
        assert qbyord == q1

    def testSwap(self):
        st = Set("Test Set", 1)
        q1 = Question("What is the answer?",
                ["foo", "bar", "baz", "42"], "d", st, 1)
        q2 = Question("What is the answer to this one?",
                ["foo", "bar", "42", "quux"], "c", st, 2)
        swapRows(q1, q2)
        assert q1.getOrder() == 2
        assert q2.getOrder() == 1

    def testInsertQuestion(self):
        st = Set("Test Set", 1)
        q1 = Question("What is the answer?",
                ["foo", "bar", "baz", "42"], "d", st, 0)
        q2 = Question("What is the answer to this one?",
                ["foo", "bar", "42", "quux"], "c", st, 1)
        q3 = Question("And how about this one?",
                ["foo", "bar", "42", "quux"], "c", st, 2)
        q4 = Question("And just one more.",
                ["foo", "bar", "42", "quux"], "c", st, 3)

        # we'll need to refetch because the ords have been changed in a
        # separate instance of the question; now the ords will be in order,
        # so sort by order and check the order of their qids
        q1id, q2id, q3id, q4id = \
                q1.getQid(), q2.getQid(), q3.getQid(), q4.getQid()
        insertQuestion(q3, 1)
        newQs = getBySet(st)
        newQs.sort(key=lambda question: question.getOrder())
        assert newQs[0].getQid() == q1id
        assert newQs[1].getQid() == q3id
        assert newQs[2].getQid() == q2id
        assert newQs[3].getQid() == q4id


    def testDelete(self):
        st = Set("Test Set", 1)
        q1 = Question("What is the answer?",
                ["foo", "bar", "baz", "42"], "d", st, 1)
        q2 = Question("What is the answer to this one?",
                ["foo", "bar", "42", "quux"], "c", st, 2)
        q3 = Question("What is the answer to another one?",
                ["foo", "bar", "42", "quux"], "c", st, 2)

        qm = QuestionManager(st)
        qs_from_qm = [i for i in qm]
        assert len(qs_from_qm) == 3

        # bare delete outside of qm (not generally a good idea)
        q3.delete()
        # we haven't updated question manager yet
        qs_from_qm = [i for i in qm]
        assert len(qs_from_qm) == 3
        # now...
        qm.update()
        qs_from_qm = [i for i in qm]
        assert len(qs_from_qm) == 2

        # now delete one properly thru the qm
        qm.rmQuestion(q2)
        qs_from_qm = [i for i in qm]
        assert len(qs_from_qm) == 1

    def testFindNextOrd(self):
        st = Set("Foo set", 1)
        q1 = Question("What is the answer?",
                ["foo", "bar", "baz", "42"], "d", st, 1)
        q2 = Question("What is the answer to this one?",
                ["foo", "bar", "42", "quux"], "c", st, 2)
        q3 = Question("What is the answer to another one?",
                ["foo", "bar", "42", "quux"], "c", st, 3)

        # to make sure the where clause works
        throwOffSet = Set("Bar set", 2)
        q4 = Question("And how about this?",
                ["foo", "bar", "42", "quux"], "c", throwOffSet, 5)

        o = findNextOrd(st)
        assert o == 4, "Wrong next ord, expected 4, got %i" % o

    def testRandomize(self):
        st = Set("Foo set", 1)
        q = Question("What is 2 + 2?",
                ["1", "2", "3", "4"], "d", st, 1)

        # check that order changes and correct answer stays the same. since it
        # could randomly not change the choice, run it a few times; for 0.25
        # chance of not doing anything, chance of passing incorrectly < 1^-12.
        hasChangedOrder = False
        origOrder = q._a[:]
        for i in range(20):
            q.randomizeChoices()
            indices = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4}
            assert q._a.index("4") == indices[q.getCorrectAnswer()]
            if q._a != origOrder:
                hasChangedOrder = True
        assert hasChangedOrder


if __name__ == "__main__":
    unittest.main()
