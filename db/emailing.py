# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2015 Soren Bjornstad. All rights reserved.

import database as d

import smtplib
from email.mime.text import MIMEText

from db.history import HistoryItem
from db.students import studentsInClass
import db.results
import db.output

class EmailManager(object):
    """
    Sample format of required /optsDict/:

    opts = {'fromName': 'Jane Doe',
            'fromAddr': 'jane.doe@example.com',
            'subject': '[CQM $c] Results for Quiz $n',
            'body': 'This is a test. Here are your results:\n$Q',
            'hostname': 'smtp.example.com',
            'port': '465',
            'ssl': 'SSL/TLS',
            'username': 'jane.doe@example.com',
            'password': 'notReallyAPassword'
           }
       """
    def __init__(self, optsDict, cls, zid):
        self.opts = optsDict
        self.cls = cls
        self.historyItem = HistoryItem(zid)
        self.studentsList = studentsInClass(cls)
        self.connection = None

    def openSMTPConnection(self):
        hostname = self.opts['hostname']
        port = self.opts['port']
        if self.opts['ssl'] == 'SSL/TLS':
            s = smtplib.SMTP_SSL('%s:%s' % (hostname, port))
        elif self.opts['ssl'] == 'STARTTLS':
            s = smtplib.SMTP('%s:%s' % (hostname, port))
            s.ehlo()
            s.starttls()
        else:
            # connection unsecured; not likely to be used, but we support it
            s = smtplib.SMTP('%s:%s' % (hostname, port))
            s.ehlo()
        s.login(self.opts['username'], self.opts['password'])
        self.connection = s

    def closeSMTPConnection(self):
        self.connection.quit()

    def sendEmail(self, student):
        fromStr = "%s <%s>" % (self.opts['fromName'], self.opts['fromAddr'])
        toStr = "%s %s <%s>" % (
                student.getFn(), student.getLn(), student.getEmail())
        subjectStr = self._expandFormatStr(self.opts['subject'], student, False)
        emailStr = self._expandFormatStr(self.opts['body'], student, True)

        msg = MIMEText(emailStr.encode('utf-8'), _charset='utf-8')
        msg['From'] = fromStr
        msg['To'] = toStr
        msg['Subject'] = subjectStr

        if self.connection is None:
            self.openSMTPConnection()
        self.connection.sendmail(fromStr, toStr, msg.as_string())

    def getPreview(self):
        pass

    def _expandFormatStr(self, text, student, body=False):
        """
        Expand any format-string parameters in /text/, filling with values from
        self when they are global parameters, or from /student/ when specific
        to an individual student.

        If /body/ is true (default False), also expand format strings that are
        available in only the body and not the subject.

        Format strings available in subject or body:
            $c: name of current class
            $n: number of current quiz
            $s: name of student email is being sent to, as Firstname Lastname
            $S: name of student email is being sent to, as Lastname, Firstname
            $r: number correct
            $t: total number of questions
            $p: percentage correct
            $R: class average correct
            $P: class average percentage
            $$: literal dollar sign

        Format strings available in body only:
            $a: list of student's answers vs. correct (like in view dialog)
            $q: display of quiz, with correct answers
            $Q: display of quiz, with correct & student's answers

        Any $[a-zA-Z] string that is not mentioned in the above lists will be
        ignored, but for clarity, anytime you want a literal dollar sign, you
        should write `$$`.
        """

        text = text.replace('$c', self.cls.getName())
        text = text.replace('$n', "%i" % self.historyItem.seq)
        fn = student.getFn()
        ln = student.getLn()
        text = text.replace('$s', "%s %s" % (fn, ln))
        text = text.replace('$S', "%s, %s" % (ln, fn))

        results = db.results.readResults(student, self.historyItem.zid)

        resultsStats = db.results.calcCorrectValues(results)
        text = text.replace('$r', "%i" % resultsStats[0])
        text = text.replace('$t', "%i" % resultsStats[1])
        text = text.replace('$p', "%.01f" % resultsStats[2])

        # classAverages could be a performance hit, so only calculate it if
        # we're actually going to use it
        if '$R' in text or '$P' in text:
            classAverages = db.results.calcClassAverages(
                    self.studentsList, self.historyItem.zid)
            text = text.replace('$R', "%.01f" % classAverages[0])
            text = text.replace('$P', "%.01f" % classAverages[2])

        if body:
            text = text.replace('$a', _formatResultsTable(results))
            questions = self.historyItem.ql
            text = text.replace('$q', db.output.genPlainText(questions))
            text = text.replace('$Q', db.output.genPlainText(
                questions, includeStudentResults=results))

        text = text.replace('$$', '$')
        return text

def _formatResultsTable(results):
    rows = ["#\tYou\tCorrect Answer"]
    for i in results:
        #TODO: What about None? (see ui/results.py data() function)
        try:
            rows.append("%s\t%s\t%s" % (i[0], i[1].upper(), i[2].upper()))
        except AttributeError:
            # student answer is None
            rows.append("%s\t%s\t%s" % (i[0], i[1], i[2].upper()))
    return '\n'.join(rows)
