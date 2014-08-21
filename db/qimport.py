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
        self.errors = []
        self.curOrd = None

    def txtImport(self):
        """Run an import. Returns a string to display to the user containing a
        list of errors in the import."""

        with open(self.f, 'rb') as csvfile:
            dialect = csv.Sniffer().sniff(csvfile.read(1024))
            if dialect.delimiter not in ('\t', ',', ';'):
                return "Invalid delimiter detected. Please use tab, comma, " \
                       "or semicolon."
            csvfile.seek(0)
            r = csv.reader(csvfile, dialect)
            for row in r:
                self.mkQuestion(row)

        return self.errListFormat()

    def mkQuestion(self, row):
        try:
            question, a, b, c, d, e, ca = row
        except ValueError:
            self.errors.append((row[0], "Wrong number of columns for this row."))
            return
        except Exception as e:
            self.errors.append((row[0], e))

        # make ca lowercase; not doing yet to help test errors

        ansList = [i.strip() for i in [a,b,c,d,e] if i]
        try:
            self.ql.append(questions.Question(
                question, ansList, ca, self.st, self.getOrd()))
        except questions.QuestionFormatError as e:
            self.errors.append((question, e))

    def getOrd(self):
        if not self.curOrd:
            self.curOrd = questions.findNextOrd(self.st)
        else:
            self.curOrd += 1
        return self.curOrd

    def errListFormat(self):
        """Provide user with a list of problems that occurred during import."""
        errString = ""
        num = 1
        for i in self.errors:
            errString += "\n\n#%i.\nQuestion: %s\nError: %s" % (num, i[0], i[1])
            num += 1
        return errString.strip()
