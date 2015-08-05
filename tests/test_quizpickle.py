# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2015 Soren Bjornstad. All rights reserved.

import utils
import db.genquiz as gq
import db.output as op
from db.questions import Question
from db.sets import Set
from db.classes import Class

import pickle

#TODO TODO TODO: continue checking the change of renderTxt. Finish with HTML and PDF. Normalize the names of all the render fns.

class PicklingTests(utils.DbTestCase):
    def testSaveRestore(self):
        cls = Class("TestClass")
        st = Set("TestSet", 1)
        st2 = Set("RevSet", 2)
        sl = [st, st2]
        q = Question("Hello?", ["foo", "bar", "baz", "quux"], "c", st, 1) #"new"
        q2 = Question("Goodbye?", ["1", "2", "3", "4"], "d", st, 2) # "new"
        q3 = Question("Sayonara.", ["1", "2", "3", "4"], "c", st2, 2) # "review"
        ql = [q, q2, q3]

        quizNum = 1
        date = '2015-08-05' # use a datetime obj later on, format on display
        newNum = 2 #/ of course do this by checking list length in
        revNum = 1 #\ the Quiz object's lists later on
        newSet = st

        qPickle = pickle.dumps(ql)


        unPickledQl = pickle.loads(qPickle)
        #content = op.genPlainText(unPickledQl)
        op.renderTxt(unPickledQl, cls, quizNum, 'testfile.txt')
