#!/usr/bin/python

from bs4 import BeautifulSoup

IDX_QNUM = 0
IDX_QUESTION = 1
IDX_ANSWER = 2

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

    def printRepr(self):
        print "USER ID %s" % self.tpid
        for i in self.responseList:
            print "%s: %s - %s" % (i[IDX_QNUM], i[IDX_QUESTION], i[IDX_ANSWER])
        print ""

with open('toParse.html') as f:
    data = f.read()

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
        question = ''.join(question.split('. ')[1:])

        responseList.append((qNum, question, answer))
        #print "%s: %s - %s" % (qNum, question, answer)
        #print ""
    users.append(ResponsesForUser(tpid, responseList))

for i in users:
    i.printRepr()
