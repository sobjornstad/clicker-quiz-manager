<!--

This documentation is part of Clicker Quiz Manager. CQM and this manual are
copyright 2014-2015 Soren Bjornstad.

-->

# Clicker Quiz Manager: Introduction

This is the manual for the **Clicker Quiz Manager**, version 1.1.0. This
application allows you to manage classes, sets of questions, and review history
in order to generate daily quizzes for your students. CQM interfaces with
Turning Technologies’ [TurningPoint][turningpoint-website] clicker response
software (hereafter referred to as “TurningPoint”) by exporting questions to
TurningPoint and importing scores and statistics from it. If you do not have a
clicker system or want to use both clickers and another method of giving
quizzes at different times, CQM can also export quizzes in HTML, plain text, or
(with the [LaTeX][latex-wikipedia] document formatter [set up on your
system][setting-up-latex]) a print-ready PDF format.

[turningpoint-website]: http://www.turningtechnologies.com/
[latex-wikipedia]: https://en.wikipedia.org/wiki/LaTeX
[setting-up-latex]: #setting_up_latex
[introduction]: #clicker_quiz_manager:_introduction

All instructions in the manual that refer to TurningPoint were written for
version 5.3.1. Future versions will probably be similar, but details may
change, and changes in report and file formats may require updates to CQM.


# Outline

- [**Introduction**][introduction]
- [**Getting Help**][getting-help]: about this manual and context-sensitive
  help
- [**Opening, creating, and saving database
  files**](#opening_creating_and_saving_database_files)
    - [Installing and running CQM](#installing_and_running_cqm)
    - [About databases](#about_databases)
- [**The main window**][main-window]: where it all starts. Includes a summary
  of the following sections of the program.
- [**The Classes window**][classes-window]: working with several different
  classes
- [**The Sets window**][sets-window]: creating and organizing questions
    - About [question sets](#question_sets)
    - [The question editor][the-question-editor]
        - [The question list][the-question-list]
        - [The selected question area][the-selected-question-area]
- [**The Students window**][students-window]: who’s in your class?
    - [Table columns](#table_columns) in this window
    - [Editing students](#editing_students)
    - [Importing and exporting](#importing_and_exporting) students
- [**The Generate Quiz window**][generate-quiz-window]: creating and giving
  quizzes
    - [New and review sets][new-and-review-sets]
    - [Quiz options](#quiz_options)
    - [Previewing, saving, and rescheduling a quiz][preview-window]
    - [Using quizzes in TurningPoint](#using_quizzes_in_turningpoint)
        - [Importing a quiz into TurningPoint][quiz-in-tp]
        - [Polling][tp-polling] to get students’ answers
        - See also the *Importing Results* section of *The Quiz History window*.
- [**The Quiz History window**][quiz-history-window]: seeing how your students
  did
    - [Viewing a quiz](#viewing_a_quiz)
    - [Importing results][importing-results]
    - [Viewing results][quiz-results]
    - [Emailing results](#emailing_results)
        - [Email options][email-options]
- [**Preferences**][preferences-window]
- [**Miscellaneous and supplementary material**][miscellaneous]
    - [Setting up LaTeX][setting-up-latex]
    - [Keyboard shortcuts](#keyboard_shortcuts)


# Getting Help

In addition to the documentation in this manual, [context-sensitive
help][context-sensitive-help] is available – that is, you can get help on
specific interface elements directly within the program. This documentation is
available for most buttons and input fields that are not self-explanatory.

[getting-help]: #getting_help
[context-sensitive-help]: https://en.wikipedia.org/wiki/Context-sensitive_help

This help is made available in the form of tooltips or “what’s this?” help text,
depending on the type of interface element. For buttons, checkboxes, and other
items where clicking immediately takes action, tooltips are used: simply hover
the mouse cursor over the item to see the help text. For elements like text
boxes, spin boxes, and lists, which you can select without changing a value or
taking an action, “what’s this” help is used: select the item and press
**Shift+F1** to view the help text. (Depending on your computer system, there
may also be a question-mark button in the title bar of the window. If you have
this button, you can click it and then click the item you want help on.)  If in
doubt about which method to use, simply try both methods.


# Opening, creating, and saving database files

## Installing and running CQM

To start CQM, double-click on the `runcqm` file in the main program folder. (If
you are using Windows, you will first need to rename the file to `runcqm.py` so
that the computer will know to use Python to run it.)

In the current version, it’s necessary to install Python 2.7 before you can run
CQM; if you’re using Windows, you can grab the installer
[here][python-installer-windows]. You’ll also need to install a few packages
for Python, which are listed in the README file. For help with this, please
contact the developer or other technical support. In a future release, a
package that works out of the box on Windows will be added.

[python-installer-windows]: https://www.python.org/ftp/python/2.7.10/python-2.7.10.msi

## About databases

On the first run, you will be asked whether you want to create a new database;
you should take this option if you don’t have a database already. The next time
you open CQM, it will open the database you had open previously. If you want to
create a new database or switch to a different one, you can use the **Create
Database** and **Open Database** options on the file menu.

Generally, however, there is no reason to maintain multiple database files
unless you have two “universes” of classes which you will never want to share
any information between; one database file can manage multiple classes and any
number of questions.

CQM automatically saves your changes at periodic intervals as you go along, so
there is no need to save manually. When you are done working with CQM, simply
quit the program. You can change how many minutes CQM waits between saves in
the [preferences][preferences-window]; increasing the value may result in
slightly better performance at the cost of losing more work if there is a crash
or power failure.

[preferences-window]: #preferences


# The main window

[main-window]: #the_main_window

The main program window is a small window with buttons to open the windows for
each section of the program. The sections are as follows:

* [**Classes**][classes-window]: Add new classes or look at the classes you’ve
  set up. Classes store a list of the students in the class, information about
  what questions and question sets you’ve introduced, and any results you
  choose to import from TurningPoint.
* [**Question Sets**][sets-window]: Add, edit, and view your sets of questions,
  hereafter frequently called simply *sets*. A set is a group of questions
  assigned a particular name; each quiz you create takes its questions from one
  or more [*new sets* and any *review sets*][new-and-review-sets] that are due
  at the time. Any set you create can be used in any of your classes.
* [**Students**][students-window]: Edit the list of students in your classes.
  The list is used to keep track of how your students did when you [import
  results from TurningPoint][import-from-turning-point]. If you don’t want to
  import poll results from TurningPoint, adding a list of your students is not
  required.
* [**Generate Quiz**][generate-quiz-window]: Go here when you’re ready to
  create a quiz for your class. You can choose what new sets to use and how
  many questions you want on the quiz and CQM will randomly select some
  questions from the appropriate sets. Once the quiz has been generated, you
  can save it in formats suitable for [importing into
  TurningPoint][import-to-turning-point] (RTF), [printing
  out][setting-up-latex] and distributing to your students to take in class
  (PDF), or viewing on-screen or sending over the Internet (HTML). You can also
  export a plain-text version to be used any way you want.
* [**Quiz History**][quiz-history-window]: Here you can look at the quizzes
  you’ve given in the past and see what questions were on them and export RTF,
  PDF, HTML, or plain-text versions of them again. This is also where you can
  import, view, and [email results][emailing-results] imported from
  TurningPoint.

[new-and-review-sets]: #new_and_review_sets
[import-to-turning-point]: #importing_a_quiz_into_turningpoint
[import-from-turning-point]: #importing_results
[emailing-results]: #emailing_results

[classes-window]: #the_classes_window
[sets-window]: #the_sets_window
[students-window]: #the_students_window
[generate-quiz-window]: #the_generate_quiz_window
[quiz-history-window]: #the_quiz_history_window

Several other tools are available from the menus:

* **File → Create/Open Database...**: Switch databases to a new or existing
  one. This is not usually necessary; see the section on
  [databases][database-section].
* **Tools → Back Up Database...**: Export a backup copy of your database. It’s
  a good idea to back up your database regularly in case you accidentally
  delete important data and to guard against program bugs.
* **Tools → Forget Saved Passwords**: CQM has an option to save your email
  server password (see the [preferences][preferences-window] section). If there
  are security concerns or you otherwise want to be sure no saved passwords
  remain in the database, choose this option. Note that this does not disable
  the saving of passwords: the next time you enter your password, it will be
  saved again. If you want to disable it, you can do so in the preferences.
* **Tools → Preferences**: Edit [user and interface
  preferences][preferences-window].
* **Help → Manual**: Open this manual in your web browser.
* **Help → Version**: Show what version of CQM you’re using. (This is usually
  also displayed at the top of the main window.)


# The Classes window

In CQM, you create one *class* for each section that you teach. This allows you
to introduce different questions or the same questions in a different order to
each of your sections and keep track of how your students in each section did.
This also means that if you teach a class again, you can go back and see what
you did in previous years.

The Classes window is fairly straightforward. On the left is a list of all the
classes you currently have, arranged in alphabetical order; on the right you
can add new classes and rename or delete existing classes. Deleting a class
will never touch any of your question [sets][sets-window], but it will
permanently delete any [students][students-window], [review
history][quiz-history-window], and [quiz results][quiz-results] that you have
for that class, so be careful. Classes are always listed in alphabetical order.

Every class has access to all sets and questions that you have in your
database, so creating classes does not need to divide up your questions in any
way.


# The Sets window

## Question sets

A *question set* or just *set* is a group of questions that will be introduced
on a certain quiz. For instance, you might create a set called “Akkusativ” which
contains questions involving the accusative case in German. After you’ve created
this set, anytime you learn about the accusative case in one of your classes,
you can generate and give a quiz using that set.

The sets dialog (sometimes called the *sets list*) is very similar to the
classes dialog, with the addition of “move up” and “move down” buttons since
you may want to group your sets in ways other than alphabetical order; perhaps
you want to put similar topics together. If you want to move a set a long
distance, it may be more convenient to drag and drop it to its new location
than to use the buttons.

Deleting a set will delete all of its questions, and it will no longer come up
for review in any classes where it is a review set. Past quizzes that included
that set can still be viewed, although their set name is no longer available.


## The question editor

When you click the Edit button or double-click on an entry in the sets list,
you will be taken to the question editor. The question editor has two sections:
the [*question list*][the-question-list] and the [*selected question
area*][the-selected-question-area]. When you select a question in the question
list, the selected question area shows the information for that question.

[the-question-editor]: #the_question_editor
[the-question-list]: #the_question_list
[the-selected-question-area]: #the_selected_question_area

### The question list

The **New** button starts a new question and moves the focus to the [selected
question area][the-selected-question-area], while the **Delete** button deletes
the currently selected question.

The **Move Up** and **Move Down** buttons allow you to reorder the questions; as
in the set list, you can also drag and drop questions. The order that questions
appear in the question list has no bearing whatsoever on how or where they
appear in quizzes. However, changing the order might make things easier to read
(you might want to group related questions together if there are a lot of them,
for instance).

The **Import** button allows you to import questions from a CSV file, which can
be delimited with tabs, commas, or semicolons. The file should contain the
following seven columns:

* *Question*.
* *Answers A–E*, in order. If you only want to use choices A through C and
  you're using a comma as your delimiter, simply place two extra commas after
  choice C to fill the columns with blank values.
* *The correct answer* as a lowercase or uppercase letter, A through E.

When you import, you'll be advised if any of the rows in your file were invalid
or there were other problems importing, and CQM will import as much as it can.

The **Export** button doesn’t work in the current version of CQM, but it would
be the inverse of the import button if it did.

The **Generate Quiz** button has the same effect as clicking the Generate Quiz
button on the main menu, except it tries to select the question set being edited
as the new set.

The **Randomize Questions** button scrambles the order of the answer choices for
all questions in the question list (keeping the correct answer pointed to the
right choice, of course).

At the very bottom of the question list, there is a drop-down box labeled **Jump
to set**. You can use this to quickly switch to editing the questions of a
different set without closing the question editor and returning to the set list.

### The selected question area

The selected question area shows the contents of the question that you’ve
selected in the question list, or of the new question that’s being added. Since
it’s possible for questions to be invalid (for instance, if you don’t provide
any answer choices), when you edit something in the selected question area, the
rest of the dialog is disabled until you choose to save it or discard it, so
that you don’t end up with a question that doesn’t work properly. If the
question is invalid when you click the save button, you’ll be told why and how
to fix it. You can quickly save and validate your question by pressing
**Ctrl+S**.

The **Question** field is where you type in the question you want to ask. For
instance, you might enter “What color is the sky?” There are two special forms
of markup you can use here:

* To create a *multi-line question*, separate the lines of the question with
  `//` (two forward slashes with no space in between). When the quiz is
  formatted in PDF or HTML format, this will print the second part on a
  separate line in italics. You might want a second line to provide some
  clarification of the first line, or to give a translation of a question in a
  foreign language.
* To create a *blank*, write `[...]`. For instance, an alternative phrasing of
  the question suggested above could be, “The sky is [...].” This method is
  better than simply writing in some underscores (“The sky is \_\_\_\_\_\_”)
  because it ensures that your blanks will all be a consistent length, and it
  allows CQM to adjust that length to an appropriate amount for each output
  format.

Due to technical limitations, the `//` will not be rendered into a separate
line when creating a TurningPoint quiz, but the markup has been designed so
that it will remain quite readable in that format: slashes are already standard
typographical practice for indicating line breaks when they’re unavailable.

If you forget the details of this markup while you’re adding questions, a quick
reference is available in the [“What’s this?” help][getting-help] for the
question field. You can request this help by pressing **Shift+F1** with your
cursor in that field.

The **Answers** box allows you to fill in several multiple-choice answers. You
must fill in at least boxes A and B (a right and a wrong answer), but you can
fill up to five. When you’re done adding possible choices, choose the correct
answer from the Correct Answer drop-down. If you don’t have your hand on the
mouse, you can select the correct answer by pressing the Tab key to highlight
the drop-down and then pressing the key corresponding to the correct answer (A
through E).

The choices you provide will be shown on TurningPoint, HTML, and plain text
output formats, but the PDF/paper quiz format will show only the question. (This
decision was made because it’s not much more difficult to hand-grade quizzes
that have fill-in-the-blanks answers as opposed to multiple-choice answers, and
they test knowledge more effectively.)

If you would prefer to always place the correct answer in box A and then
randomize the answers after you’re finished adding answers, you may wish to set
the “auto-select answer A” option in the [preferences][preferences-window]. If
you choose this option, be careful if you create questions with a choice such
as “all of the above” – the randomize option is not smart enough to deal with
these and will happily make “all of the above” answer A. On the other hand, if
you attempt to close the dialog without randomizing the answers, you will be
warned that most of the answer choices seem to be “A”, so you don’t have to
worry about accidentally giving a quiz where all the questions have the same
answer.


# The Students window

The Students window shows information about the students in your classes. You
can choose the class to edit with the Class drop-down at the top of the window.
In general, the information in the students window should be identical to the
Participant List in TurningPoint. (If you are not using TurningPoint, there is
no need to put your students into the students window unless you want to.)

## Table columns

There are several important pieces of information about each of your students:

* **The student’s name**, so you don’t have to call your student `9a2e3b`
  everywhere in the program.
* The student’s **TurningPoint ID** (*TP ID*, *User ID*). This value is used to
  match the student in CQM with the participant and results in TurningPoint.
  This value must be unique for each student, and it must match the ID listed
  in TurningPoint for that student, or CQM will be unable to import results
  (or, worse, some students will have their scores swapped). Integers are often
  convenient IDs, but any kind of number or identifier can be used as long as
  they are unique and match the ones in TurningPoint.
* The student’s **device ID** (*TP Device*). This value should match the device
  ID printed on the back of the remote the student normally uses. This field is
  not directly used by CQM; it’s fine to use any method supported by
  TurningPoint for matching participants to remotes, as long as TurningPoint
  has the right name associated with the right remote when you take quizzes
  (and the TP ID in TurningPoint matches the ID in CQM).
* The student’s **email address**. This is used to email the student’s results.
  If you don’t plan to email results, this field is not necessary.

CQM does not currently do any validation on these fields, so it important that
you make sure the user IDs are unique and that the email addresses you provide
are correct.

## Editing students

To edit entries in the table, double-click on the cell you want to edit, or
select it and press **F2**. Once you are editing a cell, you can use the
**Tab** key to proceed to the next cell.

If you need to add or delete a lot of entries at once, you can turn on the
**Fast edit** option in the upper-right corner. When fast edit is enabled,
pressing Enter after you’ve finished entering a row will add a new row, and
clicking the Delete button will delete the row without confirmation.

## Importing and exporting

The Import and Export buttons read and write [CSV data][wp-csv] in the same
format that TurningPoint uses by default, so you can easily fill in the table
in either CQM or TurningPoint and then transfer it to the other. (If you start
in TurningPoint, you may want to add an Email column to the table there; the
data will import into CQM without an email, but you’ll still have to add the
email addresses later.) If you’d like to import data from another source, such
as a course management website or university database, you can imitate this
format. Here is an example:

    Device ID(s),Last Name,First Name,User ID,Email
    4566CE,Doe,Jane,1,janedoe@example.com
    7833EE,Doe,John,2,johndoe@example.com
    112345,"A Name with, Commas In It",Sir,3,sircommas@example.com 

[wp-csv]: https://en.wikipedia.org/wiki/Comma-separated_values

There are two bugs in TurningPoint at the time of this writing that can cause
issues unless you know how to deal with them:

* TurningPoint does not correctly escape fields containing quotation marks
  either on export or import, so make sure that you do not use them in student
  names, IDs, or email addresses. You’re probably unlikely to want them, but it
  will not be possible to export or import a valid file if you don’t observe
  this.
* When you import a students list from CQM into TurningPoint, a new “Device ID”
  column will be incorrectly added alongside the existing one. The way to fix
  this is to delete the old one (which is all the way on the left), then drag
  and drop the new one into its place.

<!-- add info on how to actually import students into TP: non-obvious -->


# The Generate Quiz window

Once you have added [at least one class][classes-window] and some [sets and
questions][sets-window], you can start creating quizzes with the **Generate
Quiz** window.

## New and review sets

Before trying to generate a quiz, it’s helpful to understand how sets relate to
quizzes. At any given time, in each class each of your sets is either a new
set or a review set:

* A *new set* has never been used on a quiz in this class; you may or may not
  want to put it on a quiz for that class in the future.
* A *review set* has previously been introduced on a quiz for this class; CQM
  will continue showing questions from that set on future quizzes in that
  class.

One good way to think about the difference is that the new sets that you choose
today will become review sets tomorrow.

A set can be a new set in some classes and a review set in other classes, since
sets are shared between classes. So we can say that in my “Fall 2015 Spanish
101” class the “Spanish Colors” set is a review set because I’ve given a quiz
on the colors earlier this semester. But in my “Fall 2015 Intro to Computer
Science” course it’s a new set, because the words for colors in Spanish have
nothing to do with computer science and so we haven’t studied (and don’t plan
to study) them.

As mentioned above, CQM keeps track of when review sets were last seen and
brings them back at regular intervals. The interval doubles after each time the
quiz is shown, so if you add a new set on your first quiz, it will be a review
set on quizzes 2, 4, 8, 16, and so on. Similarly, the new set(s) you add on
the second quiz will come back on quizzes 3, 5, 9, and 17.

## Quiz options

When you click the **Generate Quiz** button in [the main window][main-window],
you will be presented with some options for the quiz.

* At the top of the dialog you can select the **class** for which you want to
  generate a quiz. Remember that any set you create can be used in any class;
  if the *New Sets* list changes when you select a different class, that's
  because you've introduced different sets in that class so far, not because
  some sets are “part of a different class” and not available in this one.

* You can select one or more **new sets** to be introduced. You must select at
  least one new set; if you like, you can select more than one by holding down
  the Control or Shift keys.

* At the bottom of the dialog, you choose how many new questions and how many
  review questions you want to have on this quiz. The *available* display on
  the right tells you how many questions total are present in those sets. If
  you have a large number of questions in those sets, you probably don't want
  to put them all on the quiz; if you select a smaller number than the maximum
  available, CQM will pick randomly from the ones available (ensuring that at
  least one question from each new and each review set is placed on the quiz).

If you want to look at what questions are in each set in order to decide which
sets to put on the quiz, you can click the **Sets...** button and browse
through the sets and questions just as you would if you opened the set editor
from the main screen.

## Previewing, saving, and rescheduling a quiz

When you’re happy with the options you’ve selected (see above), click the
**Generate** button. CQM will give you a preview of the quiz that it's
generated. You can take a look through the questions to make sure you’re happy
with the ones it’s chosen (maybe it happened to randomly select all of the
easiest or hardest questions, or one of your two new sets got 2 questions and
the other got 5, but the first contains much more important material). If
you’re unhappy with the selections, you can click the **Return to Settings**
button and click the **Generate** button again to make new random selections.

When you're happy with the quiz as presented, it’s time to save the quiz to a
file for use. You can choose to save it as a *TurningPoint Quiz* (an RTF format
which can be imported into a question list in TurningPoint), a PDF (see
[setting up LaTeX][setting-up-latex] for information about this feature), an
HTML file, or a text file. In the case of HTML and text files, you can choose
to save with or without *answers and set names*. The easiest way to see the
difference between these is with an example.

With answers and set names:

<pre>
1. What is the most usual color for grass? (Colors)
   a. blue
   b. orange
   c. green
   d. teal
Answer: (c) green
</pre>

Without answers and set names:

<pre>
1. What is the most usual color for grass?
   a. blue
   b. orange
   c. green
   d. teal
</pre>

As you can see, one format is suitable for handing out as a quiz, while the
other is useful for studying a quiz later or for looking at as a teacher.

<a id="rescheduling_a_quiz"></a>
When you’re done saving the quiz in any formats you want, click the
**Reschedule** button. This will change the new set into a review set so that
it can come back later. It will also record an entry in the [quiz history
window][quiz-history-window], which will allow you to look at the quiz and save
it into different formats again later.

If you decide you don’t want to use the quiz after all, you can click the
**Return to Settings** button.

## Using quizzes in TurningPoint

### Importing a quiz into TurningPoint

Once you’ve exported an RTF file in the appropriate format, you can create a
question set in TurningPoint from it:

1. Start TurningPoint and click the **Content** tab.
2. Click the drop-down box titled **Content** in the upper-left corner and
   choose **New → Question List**.
3. Give the questions a name and description. If you’ve created a preset, you
   can select it from the **Use Preset** drop-down, which will adjust all the
   options under “Preferences” for you. Otherwise, adjust the options to your
   liking.
4. In the new question list, click the **Question** button in the upper-left
   corner, then choose **Import**.
5. Select the RTF file you want to import and click OK. In the resulting
   “Import Questions” dialog box, leave all the options as is and click the
   **Import** button.
6. Delete the topmost question, which is automatically created by TurningPoint
   and contains only dummy text.
7. In the lower-right corner, click **Save and Close**.

[quiz-in-tp]: #importing_a_quiz_into_turningpoint

### Polling

After importing a quiz into TurningPoint, you are ready to create the
PowerPoint and start the quiz:

1. Click the **Polling** tab at the top.
2. Select your class in the **Participants** list and the question list you
   just created in the **Content** class.
3. Click the **PowerPoint Polling** section on the right. PowerPoint will load
   and import the questions. Along with the new PowerPoint, an empty PowerPoint
   will open; you should close this without saving it.
4. Begin the slideshow to start polling.

When you finish, don’t forget to *save your session data* so that you can
import the results back into CQM. TurningPoint will prompt you to do this when
you close PowerPoint; you don’t need to save the PowerPoint file, but you do
need to save the session data. You can put the data anywhere convenient; you
will need to open it when you perform the next step, [exporting it to
CQM][importing-results].

[importing-results]: #importing_results
[tp-polling]: #polling


# The Quiz History window

The quiz history window lets you see the quizzes you’ve
[given][generate-quiz-window] in the past. For information about the columns
presented in the quiz table, see the “What’s this?” help.

## Viewing a quiz

The **View quiz** button shows the same dialog that is used to [preview a quiz
when you’re generating it][preview-window]. All of the functions work the same
way, with the exception that there is no “reschedule” button now, since the
sets have already been [rescheduled][rescheduling-a-quiz].

[preview-window]: #previewing_saving_and_rescheduling_a_quiz
[rescheduling-a-quiz]: #rescheduling_a_quiz

## Importing results

The **Import results** button allows you to import results from TurningPoint.
In order to get the results into CQM, you first need to save the session data
when you’re finished [polling][tp-polling]; TurningPoint will prompt you to do
this. It’s difficult to rename the session later, so it’s best to give the file
a helpful name like “My Class Quiz 1”. Once you have the session file, follow
these steps to import it into TurningPoint and convert it to a format that CQM
can use:

1. Click the **Manage** tab in TurningPoint.
2. In the left pane, choose your class’s participants list.
3. From the **Session** drop-down, choose **Import**. Select the session file
   and click OK.
4. If necessary, click the arrow next to your class to expand the list, then
   choose the session you just imported.
5. At the bottom-right of this window, click the **Reports** button.
6. In the upper-right of the reports screen, choose **Results by Participant**
   from the drop-down.
7. Click the **Export** button in the upper-left, then choose **HTML**. Save
   the HTML file.
8. In CQM, open the history window, select the appropriate quiz, click the
   **Import results** button, and select the HTML file you exported in step 7.

Imported results will appear in the Results window, described next.


## Viewing results

[quiz-results]: #viewing_results

The Results window, accessed by clicking the **View results** button in the
history window, lets you review how each of your [students][students-window]
did on a given quiz. Before you can use the results window, you need to [import
your results from TurningPoint][importing-results].

Like the question editor, the Results window has two panes; choosing a student
on the left will show that student’s scores and results on the right. The
student’s score is displayed at the top of the pane, and the student’s answer
to each question is shown in the table along with the correct answer. An
exclamation point in parentheses (`(!)`) is used to highlight any answers that
were wrong.

The class average is listed at the top of the window, so you can compare a
student’s score with the average or just get a general idea of how the class
did.

If you want more complex statistics, you can use the reports and statistics in
TurningPoint, which are quite extensive. However, if you look at these
statistics, you should be aware that repolling a question will result in
TurningPoint calculating your students’ scores incorrectly -- a repolled
question will result in two questions showing up in the list, and both of them
will be counted in students’ scores. CQM filters out these duplicates, counting
only the last poll for a question, so the scores in CQM should always be
accurate.

If you’d like to match up the answers listed in the results with the quiz
questions, you can click the **Show quiz** button at the bottom of the window
to open the [quiz preview][preview-window].

If you imported the results incorrectly or just don’t want to keep them in CQM
for some reason, you can delete them from the database by clicking **Delete
results**.

## Emailing results

With a paper quiz, you can easily hand graded quizzes back to your students,
letting them know how they individually did without sharing the information
with the rest of the class. With a clicker quiz taken through TurningPoint,
however, it is not obvious how to accomplish this. CQM solves this problem by
providing a function to email students their results. Each student will receive
only his or her own score and answers (and information about the class average,
if you wish). The precise format of the email and what is sent in it are very
customizable.

If a student doesn’t have any results for a quiz (for instance, if they were
absent, or they added the class after the quiz was given), a quick message will
be sent indicating that no results were recorded for that quiz number and they
should contact their instructor if they think this is wrong.

You can access the email function by clicking the **Email results** button.

### Email options

The Email Results dialog is a somewhat complicated form. For this reason, the
values you fill in will be saved until the next time you use the email function
in the same class. (Different classes have separate options, but if you want to
use exactly the same ones, you can always copy the options into a document and
paste them into the other class’s options dialog.)

[email-options]: #email_options

#### The Email section

In the top section of the dialog, you see most of the same fields that you
normally see when you write an email. The exception is that you tell CQM who
the email is coming *from* rather than who it’s going *to*. (The email
addresses the message is being sent *to* are pulled from the Email column of
the Students table for that class; before sending email for the first time,
it’s a good idea to be sure that this column is filled out and accurate.) You
can put anything you like in the **From name** field, but you should use the
email address you’re sending from in the **From address** field; some services
will allow you to send email from a different address than the one you actually
have with their service, but this doesn’t always work, and it may increase the
chances of your emails being flagged as spam.

In the **subject** and **body** fields, you can write any normal text you like,
such as a greeting or information about the class, but you should also include
some *format parameters*, which are special strings beginning with a dollar
sign that are replaced with appropriate content when the email is sent out. For
example, if you write `$n` (which represents the quiz number) in your subject
or body when sending the results for quiz 2, CQM will replace it with a `2`
when the email is sent out. Some parameters, like this one, are the same for
the whole class; others, such as `$f` (first name) and `$p` (student’s percent
correct), are specific to individual students and will be evaluated separately
for each student emailed.

A full listing of format parameters follows. These parameters are available in
both the subject and the body fields:

* **$$**: a literal dollar sign (that is, if you actually want a dollar sign to
  appear in the text of your final email, instead of having it form part of a
  format parameter, write `$$` instead of `$`)
* **$c**: the name of the current class
* **$n**: the number of this quiz
* **$f**: the student’s first name
* **$l**: the student’s last name (lowercase ell)
* **$s**: the student’s name formatted as *Firstname Lastname*
* **$S**: the student’s name formatted as *Lastname, Firstname*
* **$r**: the number of questions the student got correct on this quiz
* **$t**: the total number of questions on this quiz
* **$p**: the student’s percentage grade on this quiz (equivalent to 100 times
  `$r` divided by `$t`, to two decimal places)
* **$R**: the class’s average number of questions correct
* **$T**: same as `$t` (this is primarily supported in case you type it by
  mistake)
* **$P**: the class’s average percentage

These parameters are available only in the body field, because they are
multiple lines long and would not make sense in the subject field:

* **$a**: A table of the student’s answer choices and the correct choices. This
  is basically the same as the table shown in the Results dialog.
* **$q**: A listing of the questions on the quiz; this looks the same as the
  [quiz preview][preview-window] accessible in the quiz history or generate
  quiz windows.
* **$Q**: Like `$q`, but includes the student’s answers along with the correct
  answers.

Format parameters that don’t match any of these sequences will be sent on in
the email exactly as they are (so if you write `$Z`, your email will contain an
actual `$Z` when your students receive it).

If you don’t want to memorize all these format parameters, you’ll be happy to
know that a quick reference is available in the “What’s this?” help of the Body
field (press **Shift-F1** while editing).

Here’s an example of one way you could write the body of your email:

    Hi $f,

    You scored $r/$t ($p%) on quiz $n; the class average was $R/$t. Here is an annotated version of the quiz:

    $Q

    See you in class soon!


#### The SMTP server section

CQM does not have any kind of central server that can send out email, so you
need to provide it with the information for an SMTP ([Simple Mail Transfer
Protocol][smtp-wp]) server that can be used to send the mail. The good news is
that if you have any kind of email account, you probably have access to an SMTP
server. Alternatively, if you’d rather use a different email account from your
main one, you can open a new free email account; Gmail allows you to send up to
500 emails via SMTP per day (max 200 per hour), and most other services are
probably similar.

If you’re not sure what settings you need to use for your email account, you
can poke around in the help for your email service or search Google for
something like `Gmail SMTP settings`.

[smtp-wp]: https://en.wikipedia.org/wiki/Simple_Mail_Transfer_Protocol


# Preferences

You can change CQM’s preferences by choosing **Tools → Preferences** in the
[main window][main-window]. The following options are available:

* **Debug mode**: Show the debug menu and show a slightly different message
  when an error occurs. Most users can leave this off.
* **Auto-select answer A**: When adding new questions in the [question
  editor][the-question-editor], start with A selected as the correct answer
  instead of leaving the field blank. This may be useful in conjunction with
  the randomize answers button.
* **Save email passwords**: Save the password entered for the SMTP server in
  the [email options][email-options]. This is saved per class. The password
  storage has about the same level of security as the “save password” function
  on an average web browser: it is not possible to view saved passwords through
  CQM after entering them the first time, but passwords are stored in the
  database in plain text, so a serious attacker could open the database
  manually and extract the password. You can clear all saved passwords at any
  time by choosing **Tools → Forget Saved Passwords**.
* **Minutes between saves**: This controls how often CQM saves your changes
  automatically. See the section on [databases][database-section] for more
  information.
* **XeLaTeX command**: When generating PDF output, call this program on the
  LaTeX code to render the PDF. See the [setting up LaTeX][setting-up-latex]
  section for more information.

[database-section]: #about_databases

# Miscellaneous and supplementary material

[miscellaneous]: #miscellaneous_and_supplementary_material

## Setting up LaTeX

To produce PDF output, CQM requires the [LaTeX document preparation
system][latex-wikipedia] to be installed on your computer. On Linux, installing
LaTeX through your distribution’s package manager should work. On Windows, you
can [install MiKTeX][miktex-download].

[miktex-download]: http://www.miktex.org/download

Whatever your operating system, you will also need the following LaTeX packages
to create PDF quizzes with CQM: `fontspec`, `xunicode`, `geometry`, `setspace`,
`titlesec`, `microtype`, `ebgaramond`, `ifluatex`, `ifxetex`. Some of these
will probably come with any installation of LaTeX, but some may not. If you’re
using MiKTeX, you can find the “package manager” in your start menu and install
each of the packages.

If `xelatex` is not in the system `$PATH` (it probably will be on Linux, may be
on OS X, and definitely will not be on Windows unless you set it up that way),
you need to set the **XeLaTeX command** in the
[preferences][preferences-window] before trying to generate a PDF quiz, or you
will get an error indicating that the LaTeX executable could not be found.

## Keyboard shortcuts

It should be possible to use CQM with little to no mouse input once you become
familiar with it. Most buttons and fields have an underlined access character;
to activate that button or field, hold down the Alt key and press that access
character. Additionally, in the question editor, Sets dialog, and Classes
dialog, pressing Alt-L will focus the main list.
