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
        return self.emsg

class MissingStudentError(Exception):
    def __init__(self, emsg):
        self.emsg = emsg
    def __str__(self):
        return self.emsg

def readResults(stu, zid):
    """
    Return a student's responses for a quiz as a list of tuples.

    Arguments:
        user: the Student you want results for
        zid: the id of the quiz you want results for

    Return:
        A list of tuples consisting of the question number, the user's answer,
        and the correct answer for that quiz question.

        If the student doesn't have any responses at all for a quiz (maybe they
        were added to the class after the quiz was taken), return None.
    """

    # get the student's answers
    stid = stu.getStid()
    c = d.inter.exQuery('SELECT answers FROM results WHERE zid=? AND stid=?',
            (zid, stid))
    answers = c.fetchall()
    try:
        answers = json.loads(answers[0][0])
    except IndexError:
        return None

    # Get the questions so we can find the correct answer. (Note: when we run
    # this function 20 times to find the values for each student, these are
    # indeed unnecessary SELECTs and loads -- the questions will be the same
    # for all of them. I think the simplicity of interface is easily worth the
    # small performance hit for the small number of students that are normally
    # in a class.)
    c = d.inter.exQuery('SELECT qPickle FROM quizzes WHERE zid=?', (zid,))
    questions = pickle.loads(c.fetchall()[0][0])

    returnVals = []
    for (qNum, studentsAnswer) in answers:
        # As detailed in the long comment in writeResults(), we need to fetch
        # based on the question number given in the actual answers stored in
        # the results table, not how far we've gone through the loop, because
        # it's possible that a question in the quiz doesn't actually have any
        # results.
        questionText = questions[qNum-1].getCorrectAnswer()
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
        None (if everything was successful).

    Raises:
        WrongQuizError: if the questions in the response don't seem to match
            up with the questions in the quiz, throw this error unless
            suppressCheck is True.
        MissingStudentError: if no tpid can be found in the database matching
            the one in what's been imported.
    """
    stu = findStudentByTpid(response.tpid, cls)
    if stu is None:
        raise MissingStudentError("No student by ID %s is in the students table!"
                % response.tpid)

    c = d.inter.exQuery('SELECT qPickle FROM quizzes WHERE zid=?', (zid,))
    qPickle = c.fetchall()[0][0]
    ql = pickle.loads(qPickle)

    # Make sure the all the questions in the results we're importing actually
    # exist in the quiz we've matched it to, mod leading/trailing whitespace.
    # If not, we're probably importing the wrong file (and it will be
    # impossible to figure out what to match that question to, anyway).
    if not suppressCheck:
        quizQuestionList = [i.getQuestion().strip() for i in ql]
        failures = []
        for i in response.responseList:
            if i[IDX_QUESTION].strip() not in quizQuestionList:
                failures.append(i[IDX_QUESTION].strip())
        if len(failures) > 0:
            raise WrongQuizError("It looks like you're trying to import "
                    "results from the wrong quiz. The following "
                    "%i questions in the responses you imported do not exist "
                    "in the quiz you're importing into:\n\n%s\n\nPlease check "
                    "the file you're importing and the quiz you're importing "
                    "into. If they are really the same, then there is probably "
                    "a bug in the results parser; please contact the developer "
                    "for help."
                    % (len(failures), '\n'.join(failures)))

    answers = []
    for i in response.responseList:
        # We use this dictionary to find the question number *based on the
        # question text* rather than the number that TP gives us, which can be
        # flawed even with the duplicate checking routine
        # ResponsesForUser.checkForRepolls() (for instance, if we
        # unintentionally skip a question entirely). We must add one to the
        # value because quiz question numbering starts from 1, not 0.
        lookupTable = {ql[i].getQuestion().strip(): i+1 for i in range(len(ql))}
        try:
            answer = (lookupTable[i[IDX_QUESTION]], i[IDX_ANSWER].lower())
        except AttributeError:
            # if it can't be turned lowercase, it should be None, which is also
            # perfectly valid here
            assert i[IDX_ANSWER] is None
            answer = (i[IDX_QNUM], i[IDX_ANSWER])
        answers.append(answer)
    answers.sort(key=lambda i: i[0])
    q = '''INSERT INTO results (rid, zid, stid, answers)
           VALUES (null, ?, ?, ?)'''
    vals = (zid, stu.getStid(), json.dumps(answers))
    d.inter.exQuery(q, vals)

def delResults(zid):
    """
    Remove a set of results from the database. This could be useful if an
    error occurred in the middle of an import (damn transactions not being
    usable with this database framework) or if the user discovers she did
    something wrong or wants to completely redo the results set.

    As far as I can think of, nothing relies on results besides results (and
    emailing results, but that doesn't leave any state in the database), so
    deleting results should be perfectly safe at any time.
    """

    d.inter.exQuery('DELETE FROM results WHERE zid=?', (zid,))
    d.inter.checkAutosave()


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

        Note that the results list generated is not guaranteed to be in the
        correct order: say we repoll question 4 in position 6. It is not
        possible for this function to know from the response list that the
        question in position 6 ought to be moved before position 5. This should
        not be a problem if other functions select from the responseList
        (unordered) by the question text, which they should be doing anyway.
        """
        # first knock out the dupes
        usedQuestions = {}
        killIndices = []
        for i in range(len(self.responseList)):
            curQuestion = self.responseList[i][IDX_QUESTION]
            if curQuestion in usedQuestions:
                killIndices.append(usedQuestions[curQuestion])
            # Notice that the following overwrites a current entry if there is
            # one; that's okay because we just added it to killIndices, so
            # doing this repeatedly will still result in all of the indices
            # except the last getting killed.
            usedQuestions[curQuestion] = i

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

def calcCorrectValues(results):
    """
    Calculate the fraction and percentage correct for a student's answers.

    Arguments:
        results: The results list in standard format (from the db table).

    Return:
        A tuple: (number correct, total number of questions, float percentage)
    """

    numCorrect = 0
    for i in results:
        if i[1] == i[2]:
            numCorrect += 1
    return (numCorrect, len(results), 100 * float(numCorrect) / len(results))

def calcClassAverages(studentList, zid):
    """
    Like calcCorrectValues(), but returns the fraction/percentage correct for
    all students in the studentList rather than a single student.
    """

    allResults = []
    # in case the last student doesn't *have* results, we have to save this
    lastResultsContent = None
    for stu in studentList:
        results = readResults(stu, zid)
        if results is None:
            # there are no results for this student; ignore them
            continue
        allResults.append(calcCorrectValues(results)[0])
        lastResultsContent = results
    totalNum = len(lastResultsContent) # it should be the same for all students
    avgCorrect = float(sum(allResults)) / len(allResults)
    avgPercentage = 100 * avgCorrect / totalNum
    return (avgCorrect, totalNum, avgPercentage)
