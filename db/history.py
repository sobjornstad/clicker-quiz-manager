# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2015 Soren Bjornstad. All rights reserved.

import datetime
import pickle

import db.database as d
import db.classes

class QuizProvider(object):
    """
    Class to provide quiz questions to the quiz preview/save dialog so that it
    can save quizzes that have been previously generated. Since no rescheduling
    needs to be done at this point, a true Quiz object is not required. Thus,
    an object of this class is used and imitates Quiz in the methods that the
    PreviewDialog requires, which are fetchQuestionsForOutput() and getClass().
    """

    def __init__(self, questions, cls):
        self.cls = cls
        self.ql = questions

    def getClass(self):
        return self.cls

    def fetchQuestionsForOutput(self):
        return self.ql


class HistoryItem(object):
    """
    Unlike the rest of our data containers in this application, we're going to
    handle this one with public attributes, as this rarely needs to write back
    to the db and can mostly be an immutable container. The only thing we'll
    need to update is resultsFlag and possibly notes; we'll add setter
    functions for those when we need them.
    """

    def __init__(self, zid):
        d.cursor.execute('SELECT * FROM quizzes WHERE zid=?', (zid,))
        self.zid, self.cid, self.qPickle, self.newNum, self.revNum, \
                self.newSetNames, self.seq, self.resultsFlag, \
                self.datestamp, self.notes = d.cursor.fetchall()[0]
        self.ql = pickle.loads(self.qPickle)

    def getFormattedDate(self, dateFormat='%Y-%m-%d'):
        """
        Return the datestamp formatted with strftime(3) format string
        /dateFormat/. If no format is provided, the ISO standard YYYY-MM-DD
        format will be used.
        """

        dt = datetime.datetime.strptime(self.datestamp, '%Y-%m-%d')
        return dt.strftime(dateFormat)

    def getFormattedResultsFlag(self):
        if self.resultsFlag == 0:
            return 'Not imported'
        elif self.resultsFlag == 1:
            return 'Available'
        elif self.resultsFlag == 2:
            return 'Sent'
        else:
            assert False, "Invalid value of self.resultsFlag!"

def historyForClass(cls):
    cid = cls.getCid()
    d.cursor.execute('SELECT zid FROM quizzes WHERE cid=?', (cid,))
    quizzes = [HistoryItem(i[0]) for i in d.cursor.fetchall()]
    return quizzes
