# -* coding: utf-8 *-
# This file is part of Clicker Quiz Generator.
# Copyright 2014 Soren Bjornstad. All rights reserved.

"""
This module contains functions for creating various output formats of quizzes.

Besides two errors (LaTeXError and UnopenableError), this module provides no
classes.

Provided public functions:
    renderRTF: create an RTF object from question list and render it to file
    renderTxt: create a text string and render it to file
    genPlainText: return a text string for preview purposes
    renderHtml: create an HTML string and render it to file
    renderPdf: render provided questions to a PDF file using LaTeX
    autoOpen: automatically open given file in the OS's default program for it
    munge_latex: escape characters in string to not confuse LaTeX

Abbreviations used in this module:
    q, a, ca: question, answer, correct answer (letter)
    oQ, oA, oCA: original q, a, ca
    emsg: error message
    tfile, tdir: temporary file/directory
    cwd: current working directory
"""

import codecs
import os
import paramiko
import re
import shutil
import subprocess
import sys
import tempfile
from uuid import uuid4

# pylint doesn't see that this is used in .encode()
import rtfunicode # pylint: disable=W0611
import PyRTF as rtf

# when a cloze [...] is encountered, what is it replaced with in text formats?
OCCLUSION_OUTPUT = '_' * 8


### RTF for TurningPoint ###
def renderRTF(questions, fname):
    """
    Format and write the list of Questions to a file with name /fname/.
    """
    rtfObj = _genRtfFile(questions)
    renderer = rtf.Renderer()
    with open(fname, 'wb') as f:
        renderer.Write(rtfObj, f)

def _getRTFFormattedContent(ques, questionNum):
    "Return question data formatted for ExamView rtf file format."

    oQ = '.\t'.join([str(questionNum), ques.getQuestion()])
    oQ = oQ.replace('[...]', OCCLUSION_OUTPUT)
    curLetter = 0
    oA = []
    for ans in ques.getAnswersList():
        oA.append('.\t'.join([str(ques.qLetters[curLetter]), ans]))
        curLetter += 1
    oCA = '\t'.join(['ANS:', ques.getCorrectAnswer()])
    return oQ, oA, oCA

def _genRtfFile(questions):
    """
    Given a list of Questions, return an RTF object which contains all data and
    can be rendered when appropriate using the renderRTF() function in this
    module.
    """

    doc = rtf.Document()
    section = rtf.Section()
    doc.Sections.append(section)

    section.append("MULTIPLE CHOICE")
    section.append("")
    qNum = 1
    for question in questions:
        q, a, ca = _getRTFFormattedContent(question, qNum)

        q = q.encode('rtfunicode')
        q = q.replace('\\u9?', '\t')
        ca = ca.encode('rtfunicode')
        ca = ca.replace('\\u9?', '\t')

        section.append(q)
        for ans in a:
            ans = ans.encode('rtfunicode')
            ans = ans.replace('\\u9?', '\t')
            section.append(ans)
        section.append(ca)
        qNum += 1

    return doc


### Plain text ###
def genPlainText(questions, forQuiz=False, includeStudentResults=None):
    """
    Return a plain text string of the list of Questions (for preview or
    export). If /forQuiz/, do not include set names and correct answers;
    otherwise, do.

    If /includeStudentResults/ is set, include the answers in the results list
    underneath the correct answers. If includeStudentResults is not None,
    forQuiz is implied False.

    This function is used by renderTxt, but it can also be called alone to
    generate a preview of a quiz.
    """
    indices = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4}
    letters = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e'}
    if includeStudentResults is not None:
        forQuiz = False # by implication
        # dictionary from question number to results tuple
        lookupTable = {qTuple[0]: qTuple for qTuple in includeStudentResults}

    prev = []
    qNum = 1
    for question in questions:
        q = '. '.join([str(qNum), question.getQuestion()])
        q = q.replace('[...]', OCCLUSION_OUTPUT)
        a = question.getAnswersList()
        ca = question.getCorrectAnswer()
        try:
            st = question.getSet().getName()
        except AttributeError as e:
            if "'NoneType' object has no attribute 'getName'" in e:
                # this comes up if we're viewing a past quiz that uses a set
                # that has since been deleted
                st = "(set deleted)"

        if forQuiz:
            prev.append("%s" % q)
        else:
            prev.append("%s (%s)" % (q, st))

        letterNum = 0
        for ans in a:
            prev.append("\t%s. %s" % (letters[letterNum], ans))
            letterNum += 1

        stuAnswer = None
        if includeStudentResults is not None:
            correctAnswerText = a[indices[question.getCorrectAnswer()]]
            try:
                answer = lookupTable[qNum][1]
            except KeyError:
                # nobody in the class answered this question
                stuAnswer = "[This question was not polled and is not "\
                            "counted in your score.]"
            else:
                try:
                    studentAnswerText = a[indices[lookupTable[qNum][1]]]
                except KeyError:
                    # class answered, but student didn't
                    stuAnswer = "[You did not answer this question.] (!)"

            ca = "Answer: (%s) %s" % (ca, correctAnswerText)
            if stuAnswer is None:
                stuAnswer = "Your answer: (%s) %s %s" % (
                        answer, studentAnswerText,
                        "(!)" if studentAnswerText != correctAnswerText else "")
            prev.append(ca + '\n' + stuAnswer + '\n')
        elif not forQuiz:
            correctAnswerText = a[indices[question.getCorrectAnswer()]]
            ca = "Answer: (%s) %s" % (ca, correctAnswerText)
            prev.append(ca + '\n')
        else:
            prev.append('')

        qNum += 1
    return '\n'.join(prev)

def renderTxt(questions, cls, quizNum, filename, forQuiz=False):
    """
    Render a text string created by genPlainText() to file /filename/.

    Arguments:
        questions: list of quiz questions to be rendered
        cls: Class object that this quiz is being generated for
        quizNum: which quiz this is (lastSet in classes table)
        filename: name of the file to write the contents to
        forQuiz: if True, do not include set names and correct answers;
            otherwise, do.
    """
    content = genPlainText(questions, forQuiz)
    className = cls.getName()
    title = "%s, Quiz %i" % (className, quizNum)
    title = title + '\n' + ('-' * len(title)) + '\n\n'
    with codecs.open(filename, 'wb', 'utf-8') as f:
        f.write(title)
        f.write(content)


### HTML ###
DEFAULT_HTML_HEADER = 'db/resources/html_header_default.html'
DEFAULT_HTML_FOOTER = 'db/resources/html_footer_default.html'

def _htmlText(questions, forQuiz=False):
    """
    Given a list of Questions, return quiz as a string of HTML, very similar to
    the plain text version but formatted. If forQuiz, do not include set
    names and answers; otherwise, do.
    """
    indices = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4}
    letters = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e'}

    prev = []
    for question in questions:
        q = question.getQuestion()
        q = q.replace('[...]', OCCLUSION_OUTPUT)
        a = question.getAnswersList()
        ca = question.getCorrectAnswer()
        try:
            st = question.getSet().getName()
        except AttributeError as e:
            if "'NoneType' object has no attribute 'getName'" in e:
                # this comes up if we're viewing a past quiz that uses a set
                # that has since been deleted
                st = "(set deleted)"

        quesIsMultiPart = False
        qparts = q.split('//')
        if len(qparts) > 1:
            topline, botline = qparts
            topline, botline = topline.strip(), botline.strip()
            quesIsMultiPart = True

        if not forQuiz:
            if quesIsMultiPart:
                topline = "%s (%s)" % (topline, st)
            else:
                qtext = "%s (%s)" % (q, st)
        else:
            if quesIsMultiPart:
                topline = topline # noop, written for clarity
            else:
                qtext = q

        if not quesIsMultiPart:
            prev.append('<li><div class="foreign">%s</div>' % qtext)
        else:
            prev.append('<li><div class="foreign">%s</div>' \
                        '<div class="english">%s</div>' % (topline, botline))

        prev.append('<div class="answers">')
        letterNum = 0
        for ans in a:
            prev.append("%s. %s<br>" % (letters[letterNum], ans))
            letterNum += 1
        prev.append('</div>')

        if not forQuiz:
            correctAnswerText = a[indices[question.getCorrectAnswer()]]
            ca = '<div class="answer">Answer: <span class="answertext">' \
                    '(%s) %s</span></div>' % (ca, correctAnswerText)
            prev.append(ca + '</li>')

    return '<ol class="quiz">' + '\n'.join(prev) + '</ol>'

def renderHtml(questions, cls, quizNum, fname, forQuiz=False,
        headerPath=DEFAULT_HTML_HEADER, footerPath=DEFAULT_HTML_FOOTER):
    """
    Render a list of Questions to an HTML file.

    Arguments:
        questions: list of questions to render
        cls: Class object for the class the file is being generated for
        quizNum: which quiz this is (lastSet in classes table)
        fname: name of the file to write the contents to
        forQuiz: (optionally) if True, do not include set names or answers;
            otherwise, do. (Default False.)
        headerPath: (optionally) the path to an HTML header, which can be used
            to impose a custom format on the output (including CSS, etc.)
        footerPath: (optionally) the path to an HTML footer (usually not very
            useful except to properly finish the document).

    If no values are provided for the optional arguments, the default header
    and footer in db/resources will be used.
    """
    content = _htmlText(questions, forQuiz)

    with codecs.open(headerPath, 'r', 'utf-8') as f:
        header = f.read()
    with codecs.open(footerPath, 'r', 'utf-8') as f:
        footer = f.read()

    className = cls.getName()
    titleStr = '%s &ndash; Quiz %s' % (className, quizNum)

    header = header.replace('%%% REPLACE WITH QUIZ TITLE %%%', titleStr)
    header += '<h2>%s</h2>' % titleStr
    output = header + content + footer
    with codecs.open(fname, 'wb', 'utf-8') as f:
        f.write(output)


### PDF via LaTeX ###
DEFAULT_LATEX_HEADER = 'db/resources/latex_header_default.tex'
DEFAULT_LATEX_FOOTER = 'db/resources/latex_footer_default.tex'

class LatexError(Exception):
    """
    Indicates that an error occurred while passing input to LaTeX and
    attempting compilation.
    """
    def __init__(self, emsg):
        self.emsg = emsg
    def __str__(self):
        return repr(self.emsg)

class UnopenableError(Exception):
    """
    Indicates that CQM was unable to open a generated PDF file (when using
    autoOpen) automatically on the user's OS.
    """
    def __init__(self):
        self.emsg = "Could not open the file automatically."
    def __str__(self):
        return repr(self.emsg)

def autoOpen(path):
    """
    Open a given path with the system's automatic-filetype-detection program.
    """
    if sys.platform.startswith('linux'):
        subprocess.call(["xdg-open", path])
    elif sys.platform == "darwin":
        os.system("open %s" % path)
    elif sys.platform == "win32":
        # disabling warning: this function is not available in my dev
        # environment, but it is correct on Windows
        os.startfile(path) #pylint: disable=E1101
    else:
        raise UnopenableError

def renderPdf(questions, cls, quiznum,
        headerPath=DEFAULT_LATEX_HEADER, footerPath=DEFAULT_LATEX_FOOTER,
        latexCommand='xelatex', serverOpts=None,
        doOpen=True, doCopy=False, copyTo=None):
    """
    Create a PDF of a quiz to be printed out using LaTeX. XeLaTeX must be
    properly installed on the user's machine -- it is called through PATH.
    (TODO: Add a preference to modify the path to the LaTeX executable.)

    Arguments:
        questions: list of Questions on the quiz
        cls: Class object for class the quiz belongs to
        quizNum: which quiz this is (lastSet in classes table)
        headerPath: (optionally) the path to a LaTeX header, which can be used
            to impose a custom format on the output
        footerPath: (optionally) the path to a LaTeX footer (usually not very
            useful except to properly finish the document).
        latexCommand: (optionally) path to the executable location of the LaTeX
            parser we want to use (default 'xelatex')
        serverOpts: (optionally) Dictionary with options 'hostname', 'username',
            and 'password' for connecting to a LaTeX server. Setting this
            option to anything enables using the server. latexCommand is
            not meaningful and is ignored if using this option.
        doOpen: (optionally) whether to open the PDF automatically upon render
            (default True)
        doCopy: (optionally) whether to copy the temp-file PDF to a given
            location upon render (default False; when changing this you must
            also set copyTo)
        copyTo: (optionally) with doCopy, file path to copy the PDF to

    Returns:
        None.

    Raises:
        LatexError: if the compile failed or latexCommand could not be found.
        UnopenableError: if doOpen and automatic open failed
        AssertionError: if copyTo argument was improperly unset
    """
    latex = _prepareLaTeXString(questions, cls, quiznum, headerPath, footerPath)

    tdir = tempfile.mkdtemp()
    oldcwd = os.getcwd()
    os.chdir(tdir)

    fnamebase = "quiz"
    tfile = os.path.join(tdir, '.'.join([fnamebase, 'tex']))
    pdfFile = os.path.join(tdir, '.'.join([fnamebase, 'pdf']))
    with codecs.open(tfile, 'wb', 'utf-8') as f:
        f.write(latex)

    if serverOpts is None:
        # local compilation
        try:
            subprocess.check_output([latexCommand, '-halt-on-error', tfile])
        except subprocess.CalledProcessError as e:
            raise LatexError("LaTeX Error %i:\n\n%s" % (e.returncode, e.output))
        except OSError as e:
            raise LatexError("LaTeX Error: unable to find LaTeX executable")
        else:
            if doOpen:
                autoOpen(pdfFile)
            if doCopy:
                assert copyTo is not None, "No destination location given!"
                shutil.copyfile(pdfFile, copyTo)
        finally:
            os.chdir(oldcwd)

    else:
        # remote compilation
        localPdfFilename = '.'.join([fnamebase, 'pdf'])
        serverBasename = str(uuid4())
        serverTexFilename = '.'.join([serverBasename, 'tex'])
        serverPdfFilename = '.'.join([serverBasename, 'pdf'])

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) # change later?
        ssh.connect(serverOpts['hostname'],
                    username=serverOpts['username'],
                    password=serverOpts['password'])

        ftp = ssh.open_sftp()
        ftp.put(tfile, serverTexFilename)

        stdin, stdout, stderr = ssh.exec_command(
                'remote-latex.sh ' + serverBasename)
        print "stdout:\n", stdout.readlines()
        print "stderr:\n", stderr.readlines()

        ftp.get(serverPdfFilename, localPdfFilename)
        ftp.close()

        ssh.exec_command('remote-latex-cleanup.sh ' + serverBasename)
        ssh.close()

        if doOpen:
            autoOpen(localPdfFilename)
        if doCopy:
            assert copyTo is not None, "No destination location given!"
            shutil.copyfile(localPdfFilename, copyTo)
        os.chdir(oldcwd)

    # ignore errors: it's not worth being a bother when we're just leaving a
    # temporary file lying around
    # TODO: COMMENTED OUT because it's deleting the file before the pdf viewer
    # gets to it! Ideally we would have some framework that could zap it when
    # the program closed. I think Anki handles this by having a global temp
    # folder for the whole program that can be accessed -- we could do this in
    # database.py.

    # shutil.rmtree(tdir, ignore_errors=True)

def munge_latex(s):
    "Escape characters reserved by LaTeX in string /s/."

    # This escapes all special chars listed as catcodes in /The TeXbook/, p.37.
    # Note that spacing is not guaranteed correct with things like the tilde
    # and caret. However, those are not very likely to come up; we just don't
    # want the whole thing to crash if it does.
    s = s.replace('\\', '\\textbackslash ')
    s = s.replace('{', '\\{')
    s = s.replace('}', '\\}')
    s = s.replace('$', '\\$')
    s = s.replace('&', '\\&')
    s = s.replace('#', '\\#')
    s = s.replace('^', '\\textasciicircum ')
    s = s.replace('_', '\\textunderscore ')
    s = s.replace('~', '\\textasciitilde ')
    s = s.replace('%', '\\%')

    # Take care of straight quotation marks (single & double). Note that it's
    # not possible to handle single quotation marks correctly, as there's no
    # way to tell if it's an apostrophe or opening single quote. If you want it
    # right with singles, you need to use curlies in the question.
    s = re.sub('"(.*?)"', "``\\1''", s)

    return s

def _prepareLaTeXString(questions, cls, quizNum, headerPath, footerPath):
    """
    Prepare a quiz string to be passed to the input of LaTeX.

    Arguments:
        questions: list of Questions
        cls: Class object for the class the file is being generated for
        quizNum: which quiz this is (lastSet in classes table)
        headerPath: optionally, the path to a LaTeX header, which can be used
            to impose a custom format on the output
        footerPath: optionally, the path to a LaTeX footer (usually not very
            useful except to properly finish the document).

    This function is called from renderPdf().
    """
    text = []
    qNum = 1
    for ques in questions:
        q = ques.getQuestion()
        quesIsMultiPart = False

        q = munge_latex(q)
        q = q.replace('[...]', '\\blank')
        qparts = q.split('//')
        if len(qparts) > 1:
            topline, botline = qparts
            topline, botline = topline.strip(), botline.strip()
            quesIsMultiPart = True

        # TODO: Handle using the \ten escape sequence here
        if quesIsMultiPart:
            txt = '\\doublequestion{%i}{%s}{%s}' % (qNum, topline, botline)
        else:
            txt = '\\singlequestion{%i}{%s}' % (qNum, q)

        text.append(txt)
        qNum += 1

    with codecs.open(headerPath, 'r', 'utf-8') as f:
        header = f.read()
    with codecs.open(footerPath, 'r', 'utf-8') as f:
        footer = f.read()

    className = cls.getName()
    header = header.replace('%%% INSERT CLASS HEADER HERE %%%',
            '\\header{%s}{%s}' % (className, 'Quiz %i' % quizNum))
    return header + '\n\n' + '\n\n'.join(text) + '\n\n' + footer
