# -*- coding: utf-8 -*-

import pickle
from sqlite3 import Binary

from nose.plugins.attrib import attr
import tests.utils as utils
from db.emailing import *
from db.questions import Question
from db.sets import Set
from db.students import Student
from db.results import parseHtmlString, writeResults, MissingStudentError
import db.classes

class EmailingTests(utils.DbTestCase):
    @attr('slow')
    def testFormatter(self):
        # set up a quiz with results
        cls = db.classes.Class.createNew("TestClass (no pun intended)")
        st = Set("fooset", 1)
        s = Student.createNew("Bjornstad", "Soren", "2", "c56al", "acts+emailTesting@sorenbjornstad.com", cls)
        s2 = Student.createNew("Almzead", "Maud,Her", "5", "55655", "invalid@example.com", cls)
        q1 = Question(u"das Buch", ['hourglass', 'book', 'Bach', 'cat'], 'b', st, 1)
        q2 = Question(u"die Lieblingsfarbe", ['favorite class', 'computer', 'color', 'favorite color'], 'd', st, 1)
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
        vals = (1, cls.getCid(), Binary(qPickle), 8, 2, "Foobar", 1,
                0, '2015-08-01', '')
        d.inter.exQuery(q, vals)
        with open('tests/resources/tpStatsParse/mamasoren1.html') as f:
            data = f.read()
        responses = parseHtmlString(data)
        # we don't have a student with an ID of 1 in the db yet, so there's
        # nothing to match the one in the responses string with
        with self.assertRaises(MissingStudentError) as e:
            for resp in responses:
                writeResults(resp, cls, 1)
        # now fix that.
        s3 = Student.createNew("Bjornstad", "Jennifer", "1", "55655", "invalid2@example.com", cls)
        for resp in responses:
            writeResults(resp, cls, 1)

        # now try some formatting things.
        optsDict = {'fromName': 'Testy Tester',
                    'fromAddr': 'tester@example.com',
                    'subject': '[CQM $c] Quiz $n for $s: $r/$t ($p%)',
                    'body': 'Table of scores:\n$a\n\nAnnotated quiz:\n$Q\n\n'
                            'Original quiz:\n$q\n\nThe class average was '
                            '$R/$t ($P%). You won $$2 from your scores! '
                            'To clarify, $$roll this.',
                    'hostname': 'mail.messagingengine.com',
                    'port': '465',
                    'ssl': 'SSL/TLS',
                    'username': 'someone@fastmail.com',
                    'password': 'notMyPassword',
                    #TODO: make sure this username/pass doesn't stay in here!
                   }
        em = EmailManager(optsDict, cls, 1)
        assert em._expandFormatStr(optsDict['body'], s3, True).strip() == \
                correctFormatStrTest.strip()
        assert em._expandFormatStr(optsDict['subject'], s3, False).strip() == \
                correctFormatStrSubjTest.strip()
        #em.sendEmail(s) # do both of those things for real, and more
        #em.closeSMTPConnection()
        #assert False


correctFormatStrSubjTest = "[CQM TestClass (no pun intended)] Quiz 1 for Jennifer Bjornstad: 2/10 (20.0%)"

correctFormatStrTest = u"""
Table of scores:
#	You	Correct Answer
1	A	B
2	D	D
3	None	D
4	A	A
5	B	C
6	C	D
7	D	B
8	B	D
9	D	C
10	C	A

Annotated quiz:
1. das Buch (fooset)
	a. hourglass
	b. book
	c. Bach
	d. cat
Answer: (b) book
Your answer: (a) hourglass (!)

2. die Lieblingsfarbe (fooset)
	a. favorite class
	b. computer
	c. color
	d. favorite color
Answer: (d) favorite color
Your answer: (d) favorite color 

3. die Tür (fooset)
	a. aa
	b. bb
	c. cc
	d. dd
Answer: (d) dd
Your answer: (None) None (!)

4. der Familienname (fooset)
	a. aa
	b. bb
	c. cc
	d. dd
Answer: (a) aa
Your answer: (a) aa 

5. das Auto (fooset)
	a. aa
	b. bb
	c. cc
	d. dd
Answer: (c) cc
Your answer: (b) bb (!)

6. der Ball (fooset)
	a. aa
	b. bb
	c. cc
	d. dd
Answer: (d) dd
Your answer: (c) cc (!)

7. der Stift (fooset)
	a. aa
	b. bb
	c. cc
	d. dd
Answer: (b) bb
Your answer: (d) dd (!)

8. die Tafel (fooset)
	a. aa
	b. bb
	c. cc
	d. dd
Answer: (d) dd
Your answer: (b) bb (!)

9. der Deutschkurs (fooset)
	a. aa
	b. bb
	c. cc
	d. dd
Answer: (c) cc
Your answer: (d) dd (!)

10. der Fußball (fooset)
	a. aa
	b. bb
	c. cc
	d. dd
Answer: (a) aa
Your answer: (c) cc (!)


Original quiz:
1. das Buch (fooset)
	a. hourglass
	b. book
	c. Bach
	d. cat
Answer: (b) book

2. die Lieblingsfarbe (fooset)
	a. favorite class
	b. computer
	c. color
	d. favorite color
Answer: (d) favorite color

3. die Tür (fooset)
	a. aa
	b. bb
	c. cc
	d. dd
Answer: (d) dd

4. der Familienname (fooset)
	a. aa
	b. bb
	c. cc
	d. dd
Answer: (a) aa

5. das Auto (fooset)
	a. aa
	b. bb
	c. cc
	d. dd
Answer: (c) cc

6. der Ball (fooset)
	a. aa
	b. bb
	c. cc
	d. dd
Answer: (d) dd

7. der Stift (fooset)
	a. aa
	b. bb
	c. cc
	d. dd
Answer: (b) bb

8. die Tafel (fooset)
	a. aa
	b. bb
	c. cc
	d. dd
Answer: (d) dd

9. der Deutschkurs (fooset)
	a. aa
	b. bb
	c. cc
	d. dd
Answer: (c) cc

10. der Fußball (fooset)
	a. aa
	b. bb
	c. cc
	d. dd
Answer: (a) aa


The class average was 1.5/10 (15.0%). You won $2 from your scores! To clarify, $roll this.
""".strip()
