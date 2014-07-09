from db.questions import *
import utils

class QuestionTests(utils.DbTestCase):
    def testGettersSetters(self):
        # compile a sample question
        q = "What is Maud's family name?"
        a = ["Bethamer", "Thorne", "Almzead", "Jallwei"]
        ca = "c"
        order = 1
        sid = 1
        ques = Question(q, a, ca, sid, order)

        # make sure getters work
        assert ques.getQuestion() == q
        assert ques.getAnswersList() == a
        assert ques.getCorrectAnswer() == ca
        assert ques.getSid() == sid
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
        q = Question("Hello?", ["foo", "bar", "baz", "quux"], "c", 1, 1)
        qid = q.getQid()

        # read back in, make sure they're the same
        q2 = getById(qid)
        assert q == q2

    def testOutput(self):
        q = Question("Hello?", ["foo", "bar", "baz", "quux"], "c", 1, 1)
        q2 = Question("Goodbye?", ["1", "2", "3", "4"], "d", 1, 2)
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

if __name__ == "__main__":
    unittest.main()
