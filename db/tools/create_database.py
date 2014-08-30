#!/usr/bin/python
# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2014 Soren Bjornstad. All rights reserved.

import sqlite3 as sqlite

def makeDatabase(fname):
    connection = sqlite.connect(fname)
    cursor = connection.cursor()
    cursor.execute('CREATE TABLE questions (qid INTEGER PRIMARY KEY, ord INTEGER, q TEXT, ca TEXT, answers TEXT, sid INTEGER)')
    cursor.execute('CREATE TABLE classes (cid INTEGER PRIMARY KEY, name TEXT, setsUsed INTEGER)')
    cursor.execute('CREATE TABLE sets (sid INTEGER PRIMARY KEY, name TEXT, num INTEGER)')
    cursor.execute('CREATE TABLE history (hid INTEGER PRIMARY KEY, cid INTEGER, sid INTEGER, nextSet INTEGER, lastIvl INTEGER, factor INTEGER)')
    cursor.execute('CREATE TABLE conf (conf TEXT)')
    return connection

if __name__ == "__main__":
    print "Quiz Generator Database Creator - Interactive Interface"
    DATABASE = raw_input("Type the name of the new DB to init: ")
    makeDatabase(DATABASE)
