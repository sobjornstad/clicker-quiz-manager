#!/usr/bin/python
# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2014-2015 Soren Bjornstad. All rights reserved.

import pickle
import sqlite3 as sqlite

def makeDatabase(fname):
    connection = sqlite.connect(fname)
    cursor = connection.cursor()
    x = cursor.execute
    x('PRAGMA foreign_keys = ON')
    x('''CREATE TABLE classes
         (cid INTEGER PRIMARY KEY, name TEXT, setsUsed INTEGER)''')
    x('''CREATE TABLE sets
         (sid INTEGER PRIMARY KEY, name TEXT, num INTEGER)''')
    x('''CREATE TABLE questions
         (qid INTEGER PRIMARY KEY, ord INTEGER, q TEXT, ca TEXT,
          answers TEXT, sid INTEGER,
          FOREIGN KEY(sid) REFERENCES sets(sid) ON DELETE CASCADE)''')
    x('''CREATE TABLE students
         (stid INTEGER PRIMARY KEY, ln TEXT, fn TEXT, tpid TEXT,
         tpdev TEXT, email TEXT, cid INTEGER,
         FOREIGN KEY(cid) REFERENCES classes(cid) ON DELETE CASCADE)''')
    x('''CREATE TABLE history
         (hid INTEGER PRIMARY KEY, cid INTEGER, sid INTEGER,
         nextSet INTEGER, lastIvl INTEGER, factor INTEGER,
         FOREIGN KEY(cid) REFERENCES classes(cid) ON DELETE CASCADE,
         FOREIGN KEY(sid) REFERENCES sets(sid) ON DELETE CASCADE)''')
    x('''CREATE TABLE quizzes
         (zid INTEGER PRIMARY KEY, cid INTEGER, qPickle TEXT, newNum INTEGER,
          revNum INTEGER, newSetNames TEXT, seq INTEGER, resultsFlag INTEGER,
          datestamp TEXT, notes TEXT,
          FOREIGN KEY(cid) REFERENCES classes(cid) ON DELETE CASCADE)''')
    x('''CREATE TABLE results
         (rid INTEGER PRIMARY KEY, zid INTEGER, stid INTEGER, answers TEXT,
         FOREIGN KEY(zid) REFERENCES quizzes(zid) ON DELETE CASCADE,
         FOREIGN KEY(stid) REFERENCES students(stid) ON DELETE CASCADE)''')
    x('CREATE TABLE conf (conf TEXT)')
    x('INSERT INTO conf (conf) VALUES (?)', (pickle.dumps({}),))
    return connection

if __name__ == "__main__":
    print "Quiz Generator Database Creator - Interactive Interface"
    DATABASE = raw_input("Type the name of the new DB to init: ")
    makeDatabase(DATABASE)
