# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2015 Soren Bjornstad. All rights reserved.

from bs4 import BeautifulSoup
import pickle
import json

from db.students import Student, findStudentByTpid
import database as d

IDX_QNUM = 0
IDX_QUESTION = 1
IDX_ANSWER = 2

### Interaction with results database ###
class WrongQuizError(Exception):
    def __init__(self, emsg):
        self.emsg = emsg
    def __str__(self):
        return repr(self.emsg)

def readResults(stu, zid):
    """
    Return a student's responses for a quiz as a list of tuples.

    Arguments:
        user: the Student you want results for
        zid: the id of the quiz you want results for

    Return:
        A list of tuples consisting of the question number, the user's answer,
        and the correct answer for that quiz question.
    """

    # get the student's answers
    stid = stu.getStid()
    d.cursor.execute('SELECT answers FROM results WHERE zid=? AND stid=?',
            (zid, stid))
    answers = d.cursor.fetchall()
    answers = json.loads(answers[0][0])

    # Get the questions so we can find the correct answer. (Note: when we run
    # this function 20 times to find the values for each student, these are
    # indeed unnecessary SELECTs and loads -- the questions will be the same
    # for all of them. I think the simplicity of interface is easily worth the
    # small performance hit for the small number of students that are normally
    # in a class.)
    d.cursor.execute('SELECT qPickle FROM quizzes WHERE zid=?', (zid,))
    questions = pickle.loads(d.cursor.fetchall()[0][0])

    returnVals = []
    for i in range(len(answers)):
        qNum = answers[i][0]
        studentsAnswer = answers[i][1]
        questionText = questions[i].getCorrectAnswer()
        returnVals.append((qNum, studentsAnswer, questionText))
    return returnVals



def writeResults(response, cls, zid, suppressCheck=False):
    """
    Write a set of responses into the results table under the appropriate user.

    Arguments:
        response: the ResponsesForUser object
        cls: the class this quiz was in
        zid: the ID of the quiz the results are for
        suppressCheck: (optional, default False) If True, do not check to make
            sure the questions in the response match up with the questions in
            the quiz we're importing into.

    Return:
        True if everything was successful.
        False if a student by that tpid was not found in the database.

    Raises:
        WrongQuizError: if the questions in the response don't seem to match
            up with the questions in the quiz, throw this error unless
            suppressCheck is True.
    """
    stu = findStudentByTpid(response.tpid, cls)
    if stu is None:
        return False

    # do a quick check to make sure we're not clearly importing results into
    # the wrong quiz
    if not suppressCheck:
        d.cursor.execute('SELECT qPickle FROM quizzes WHERE zid=?', (zid,))
        qPickle = d.cursor.fetchall()[0][0]
        ql = pickle.loads(qPickle)
        quizQuestionList = [i.getQuestion().strip() for i in ql]
        failures = []
        for i in response.responseList:
            if i[IDX_QUESTION].strip() not in quizQuestionList:
                failures.append(i[IDX_QUESTION].strip())
        if len(failures) > 0:
            raise WrongQuizError("Heads up! It looks like you might be "
                    "importing results from the wrong quiz. The following "
                    "%i questions in the responses you imported do not exist "
                    "in the quiz you're importing into:\n\n%s"
                    % (len(failures), '\n'.join(failures)))

    answers = []
    for i in response.responseList:
        try:
            answer = (i[IDX_QNUM], i[IDX_ANSWER].lower())
        except AttributeError:
            # if it can't be turned lowercase, it should be None, which is also
            # perfectly valid here
            assert i[IDX_ANSWER] is None
            answer = (i[IDX_QNUM], i[IDX_ANSWER])
        answers.append(answer)
    q = '''INSERT INTO results (rid, zid, stid, answers)
           VALUES (null, ?, ?, ?)'''
    vals = (zid, stu.getStid(), json.dumps(answers))
    d.cursor.execute(q, vals)
    return True


### TurningPoint statistics parser ###
class ResponsesForUser(object):
    """
    Holds a user's user ID and his/her responses until they can be matched
    up with the actual user and placed into the results table.
    """

    def __init__(self, tpid, responseList):
        self.tpid = tpid
        self.responseList = responseList
        self.checkForRepolls()

    def checkForRepolls(self):
        """
        If a question is repolled, a duplicate entry is created; we of course
        want to only keep the results from the most recent run.
        """
        # first knock out the dupes
        lastQuestion = None
        killIndices = []
        for i in range(len(self.responseList)):
            curQuestion = self.responseList[i][IDX_QUESTION]
            if lastQuestion == curQuestion:
                killIndices.append(i-1)
            lastQuestion = curQuestion
        # http://stackoverflow.com/questions/31267493/
        # remove-list-of-indices-from-a-list-in-python
        map(self.responseList.__delitem__, sorted(killIndices, reverse=True))

        # Then, if we made any changes, fix the numbering; the order has not
        # changed, but these are tuples, so we have to change the whole tuple,
        # making it more complicated than it might be.
        if killIndices:
            currentQnum = 1
            for i in range(len(self.responseList)):
                qNum, question, answer = self.responseList[i]
                self.responseList[i] = (currentQnum, question, answer)
                currentQnum += 1

    def printRepr(self):
        print "USER ID %s" % self.tpid
        for i in self.responseList:
            print "%s: %s - %s" % (i[IDX_QNUM], i[IDX_QUESTION], i[IDX_ANSWER])
        print ""


def parseHtmlString(data):
    """
    Given a string of HTML output in appropriate format from TurningPoint's
    statistics display (TODO: add some details on what kind of thing we should
    be exporting), return a list of ResponsesForUser objects, one for each user
    who took the quiz, containing user IDs and the users' responses.
    """

    soup = BeautifulSoup(data, 'lxml')
    allTables = soup.find_all('table')
    goodTables = allTables[2:]

    users = []
    for i in range(0,len(goodTables),3): # step through list by threes
        info1, info2, report = goodTables[i:i+3]
        #name = info1.find_all('td')[1].text # not using name right now
        tpid = info2.get_text().split("Total Points:")[0].split("User Id:")[1]
        responseList = []
        for i in report.find_all('tr'):
            # get question number and answer
            bolds = i.find_all('b')
            if len(bolds) == 0:
                # this was the table headers row
                continue
            try:
                qNum = bolds[0].get_text()
                answer = bolds[1].get_text()
            except IndexError:
                # student didn't get an answer in for this question
                qNum = bolds[0].get_text()
                answer = None
            # remove periods from end
            qNum = qNum.split('.')[0]
            if answer is not None:
                answer = answer.split('.')[0]
            # get the question itself
            question = i.td.get_text()
            # remove question number: join ensures we won't cut out any sentences
            question = '. '.join(question.split('. ')[1:])

            responseList.append((qNum, question, answer))
            #print "%s: %s - %s" % (qNum, question, answer)
            #print ""
        users.append(ResponsesForUser(tpid, responseList))
    return users