# -*- coding: utf-8 -*-

import pickle
import sqlite3

import utils
import db.database as d
from db.results import *
from db.classes import Class
from db.sets import Set
from db.questions import Question
from db.students import Student, findStudentByTpid

class ResultsTests(utils.DbTestCase):
    def testParseAndRead(self):
        cls = Class("MyClass")
        mama = Student.createNew("Bjornstad", "Jennifer", "1", "9A2DC6",
                "jennifer@example.com", cls)
        soren = Student.createNew("Bjornstad", "Soren", "2", "9A2D9C",
                "soren@example.com", cls)
        st = Set("fooset", 1)
        q1 = Question(u"das Buch", ['aa', 'bb', 'cc', 'dd'], 'b', st, 1)
        q2 = Question(u"die Lieblingsfarbe", ['aa', 'bb', 'cc', 'dd'], 'd', st, 1)
        q3 = Question(u"die Tür", ['aa', 'bb', 'cc', 'dd'], 'd', st, 1)
        q4 = Question(u"der Familienname", ['aa', 'bb', 'cc', 'dd'], 'a', st, 1)
        q5 = Question(u"das Auto", ['aa', 'bb', 'cc', 'dd'], 'c', st, 1)
        q6 = Question(u"der Ball", ['aa', 'bb', 'cc', 'dd'], 'd', st, 1)
        q7 = Question(u"der Stift", ['aa', 'bb', 'cc', 'dd'], 'b', st, 1)
        q8 = Question(u"die Tafel", ['aa', 'bb', 'cc', 'dd'], 'd', st, 1)
        q9 = Question(u"der Deutschkurs", ['aa', 'bb', 'cc', 'dd'], 'c', st, 1)
        q10 = Question(u"der Fußball", ['aa', 'bb', 'cc', 'dd'], 'a', st, 1)
        ql = [q1, q2, q3, q4, q5, q6, q7, q8, q9, q10]
        qPickle = pickle.dumps(ql)

        # fake a quiz into the quizzes table, as it's quite complicated to do
        # otherwise
        q = '''INSERT INTO quizzes (zid, cid, qPickle, newNum, revNum, 
                   newSetNames, seq, resultsFlag, datestamp, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        vals = (1, cls.getCid(), sqlite3.Binary(qPickle), 8, 2, "Foobar", 1,
                0, '2015-08-01', '')
        d.cursor.execute(q, vals)

        with open('tests/resources/tpStatsParse/mamasoren1.html') as f:
            data = f.read()
        responses = parseHtmlString(data)

        for resp in responses:
            writeResults(resp, cls, 1)
        for resp in responses:
            writeResults(resp, cls, 1, suppressCheck=True) # check the check :)

        d.cursor.execute("SELECT * FROM results")
        answers = json.loads(d.cursor.fetchall()[0][3])
        assert answers[0:2] == [[1, 'a'], [2, 'd']]

        # now try to read it back
        assert str(readResults(soren, 1)) == "[(1, u'a', 'b'), (2, u'b', 'd'),"\
                " (3, u'c', 'd'), (4, u'd', 'a'), (5, u'b', 'c')," \
                " (6, u'd', 'd'), (7, u'c', 'b'), (8, u'c', 'd')," \
                " (9, u'd', 'c'), (10, u'b', 'a')]"

    def testWrongQuizError(self):
        # dupe of first part of above test, except with the wrong questions
        cls = Class("MyClass")
        mama = Student.createNew("Bjornstad", "Jennifer", "1", "9A2DC6",
                "jennifer@example.com", cls)
        soren = Student.createNew("Bjornstad", "Soren", "2", "9A2D9C",
                "soren@example.com", cls)
        st = Set("fooset", 1)
        q1 = Question(u"das Buch", ['aa', 'bb', 'cc', 'dd'], 'a', st, 1)
        q2 = Question(u"die Lieblingsfarbe", ['aa', 'bb', 'cc', 'dd'], 'a', st, 1)
        q3 = Question(u"die Tür", ['aa', 'bb', 'cc', 'dd'], 'a', st, 1)
        q4 = Question(u"der Familienname", ['aa', 'bb', 'cc', 'dd'], 'a', st, 1)
        q5 = Question(u"das Auto", ['aa', 'bb', 'cc', 'dd'], 'a', st, 1)
        q6 = Question(u"der Ball", ['aa', 'bb', 'cc', 'dd'], 'a', st, 1)
        q7 = Question(u"der Stift", ['aa', 'bb', 'cc', 'dd'], 'a', st, 1)
        q8 = Question(u"die Tafel", ['aa', 'bb', 'cc', 'dd'], 'a', st, 1)
        q9 = Question(u"this is stupid", ['aa', 'bb', 'cc', 'dd'], 'a', st, 1)
        q10 = Question(u"something wrong", ['aa', 'bb', 'cc', 'dd'], 'a', st, 1)
        ql = [q1, q2, q3, q4, q5, q6, q7, q8, q9, q10]
        qPickle = pickle.dumps(ql)

        # fake a quiz into the quizzes table, as it's quite complicated to do
        # otherwise
        q = '''INSERT INTO quizzes (zid, cid, qPickle, newNum, revNum, 
                   newSetNames, seq, resultsFlag, datestamp, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        vals = (1, cls.getCid(), sqlite3.Binary(qPickle), 8, 2, "Foobar", 1,
                0, '2015-08-01', '')
        d.cursor.execute(q, vals)

        with open('tests/resources/tpStatsParse/mamasoren1.html') as f:
            data = f.read()
        responses = parseHtmlString(data)

        with self.assertRaises(WrongQuizError) as garbage:
            for resp in responses:
                writeResults(resp, cls, 1)
