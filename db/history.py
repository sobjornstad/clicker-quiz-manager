# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2015 Soren Bjornstad. All rights reserved.

import datetime

import db.database as d
import db.classes

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
