"Module for importing questions from a tsv file."

import csv
import questions

class ImporterError(Exception):
    def __init__(self, emsg):
        self.emsg = emsg
    def __str__(self):
        return repr(self.emsg)

class Importer(object):
    def __init__(self, f, st):
        self.f = f
        self.st = st
        self.ql = []
        self.curOrd = None

    def txtImport(self):
        with open(self.f, 'rb') as csvfile:
            dialect = csv.Sniffer().sniff(csvfile.read(1024))
            csvfile.seek(0)
            r = csv.reader(csvfile, dialect)
            for row in r:
                self.mkQuestion(row)

    def mkQuestion(self, row):
        try:
            question, a, b, c, d, e, ca = row
        except Exception as e:
            raise ImporterError(e)

        # make ca lowercase; not doing yet to help test errors

        ansList = [i.strip() for i in [a,b,c,d,e] if i]
        self.ql.append(questions.Question(
            question, ansList, ca, self.st, self.getOrd()))

    def getOrd(self):
        if not self.curOrd:
            self.curOrd = questions.findNextOrd(self.st)
        else:
            self.curOrd += 1
        return self.curOrd
