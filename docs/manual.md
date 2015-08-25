<!--

This documentation is part of Clicker Quiz Manager. CQM and this manual are
copyright 2014-2015 Soren Bjornstad.

-->

# Table of Contents

- [Introduction](#introduction)
- [Creating a database](#creating_a_database)
    - [Subitem](http://www.google.com)


<a id="introduction"></a>
# Introduction & How To Get Help

This is the manual for the **Clicker Quiz Manager**, version 1.1.0. The
application allows you to manage classes, sets of questions, and review history
in order to generate daily clicker quizzes for your students. CQM interfaces
with Turning Technologies’ *TurningPoint* software (hereafter referred to as
“TurningPoint”), exporting questions and importing the results.

In addition to the documentation in this manual, context-sensitive help is
available – that is, you can get help on specific interface elements directly
within the program. This documentation is available for most buttons and input
fields that are not self-explanatory.

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

To run CQM, double-click on the `runcqm` file in the main program folder.
(If you are using Windows, you will first need to rename the file to
`runcqm.py` so that the computer will know to use Python to run it.)

On the first run, you will be asked whether you want to create a new database;
you should take this option if you don’t have one already. The next time you
open CQM, it will open the database you had open previously. If you want to
create a new database or switch to a different one, you can use the **Create
Database** and **Open Database** options on the file menu.

Generally, however, there is no reason to maintain multiple database files
unless you have two “universes” of classes which you will never want to share
any information between: one database file can manage multiple classes and any
number of questions.

CQM automatically saves your changes at periodic intervals as you go along, so
there is no need to save manually. When you are done working with CQM for the
moment, simply quit the program. You can change how many minutes CQM waits
between saves in the preferences; increasing the value may result in slightly
better performance at the cost of losing more work if there is a crash or power
failure.


# The main window

The main program window is a small window with buttons to open the windows for
each section of the program. The sections are as follows:

* **Classes**: Add new classes or look at the classes you’ve set up. Classes
  store a list of the students in the class, information about what questions
  and question sets you’ve introduced, and any results you choose to import from
  TurningPoint.
* **Question Sets**: Add, edit, and view your sets of questions, hereafter
  frequently called simply *sets*. A set is a group of questions assigned a
  particular name; each quiz you create takes its questions from one or more
  *new sets* and any *review sets* that are due at the time. Sets can be used
  from any of your classes.
* **Students**: Edit the list of students in your classes. The list is used to
  keep track of how your students did when you import results from TurningPoint.
  If you don’t want to import poll results from TurningPoint, adding a list of
  your students is not required.
* **Generate Quiz**: Go here when you’re ready to create a quiz for your class.
  You can choose what new sets to use and how many questions you want on the
  quiz and CQM will randomly select some questions from the appropriate sets.
  Once the quiz has been generated, you can save it in formats suitable for
  importing into TurningPoint (RTF), printing out and distributing to your
  students to take in class (PDF), or viewing on-screen or sending over the
  Internet (HTML). You can also export a plain-text version to be used any way
  you want.
* **Quiz History**: Here you can look at the quizzes you’ve given in the past
  and see what questions were on them and export RTF, PDF, HTML, or plain-text
  versions of them again. This is also where you can import, view, and email
  imported results from TurningPoint.

Several other tools are available from the menus:

* **File → Create/Open Database...**: Switch databases to a new or existing
  one. See the flibbertygibberty section: this is not usually necessary.
* **Tools → Back Up Database...**: Export a backup copy of your database. It’s
  a good idea to back up your database regularly in case you accidentally
  delete important data and to guard against program bugs.
* **Tools → Forget Saved Passwords**: CQM has an option to save your email
  server password (see ...). If there are security concerns or you otherwise
  want to be sure no saved passwords remain in the database, choose this
  option. Note that this does not disable the saving of passwords: the next
  time you enter your password, it will be saved again. If you want to disable
  it, you can do so in the preferences.
* **Tools → Preferences**: Edit user and interface preferences; see ....
* **Help → Manual**: Open this manual in your web browser.
* **Help → Version**: Show the version of CQM you’re using.


# The Classes window

In CQM, you create one class for each section that you teach. This allows you to
introduce different questions or the same questions in a different order to each
of your sections and keep track of how your students in each section did. If you
keep the old classes around, you can also go back and see what you did in
previous years if you teach that class again.

The Classes window is fairly straightforward. On the left is a list of all the
classes you currently have, arranged in alphabetical order; on the right you can
add new classes and rename or delete existing classes. Deleting a class will
never touch any of your questions, but it will permanently delete any students,
review history, and quiz results that you have for that class, so be careful.
Classes are always listed in alphabetical order.

Any class may use any questions that you have in your database, so creating
classes does not need to divide up your questions in any way.


# The Sets window

## Question sets

A *question set* or just *set* is a group of questions that will be introduced
on a certain quiz. For instance, you might create a set called “Akkusativ” which
contains questions involving the accusative case in German. After you’ve created
this set, anytime you learn about the accusative case in one of your classes,
you can create and give a quiz using that set.

The sets dialog (sometimes called the *sets list*) is very similar to the
classes dialog, with the addition of “move up” and “move down” buttons since you
may want to group your sets in ways other than alphabetical order; perhaps you
want to put similar topics together. If you want to move a lot of sets a long
distance, it may be more convenient to drag and drop the entries instead of
using the buttons.

Deleting a set will delete all of its questions, but will not touch your review
history. To be honest, I'm completely uncertain as to what will happen if you
delete a set that has review history, though, so don't do that yet.

## The question editor

When you click the Edit button or double-click on an entry in the list of sets,
you will be taken to the question editor. The question editor has two sections:
the *question list* and the *selected question* area. When you select a question
in the question list, the selected question area shows the information for that
question.

### The selected question area

Since it’s possible for questions to be invalid (for instance, if you don’t
provide any answer choices), when you edit something in the selected question
area, the rest of the dialog is disabled until you choose to save it or discard
it, so that you don’t end up with a question that doesn’t work properly. If the
question is invalid when you click the save button, you’ll be told why and how
to fix it. You can quickly save and validate your question by pressing
**Ctrl+S**.

The **Question** field is where you type in the question you want to ask. For
instance, you might enter “What color is the sky?” There are two special forms
of markup you can use here:

* To create a *multi-line question*, separate the lines of the question with
  `//` (two forward slashes with no space in between). When the quiz is
  formatted in PDF or HTML format, this will print the second part on a separate
  line in italics. You might want a second line to provide some clarification of
  the first line, or to give a translation of a question in a foreign language.
* To create a *blank*, write `[...]`. For instance, an alternative phrasing of
  the question suggested above could be, “The sky is [...].” This method is
  better than simply writing in some underscores (“The sky is \_\_\_\_\_\_”)
  because it ensures that your blanks will all be a consistent length, and
  allows CQM to adjust that length to an appropriate amount for each output
  format.

If you forget what markup you can use, a quick reference is available in the
“What’s this?” help for the question field. You can request this help by
pressing **Shift+F1** with your cursor in that field.

The **Answers** box allows you to fill in several multiple-choice answers. You
must fill in at least boxes A and B (a right and a wrong answer), but you can
fill up to five. When you’re done adding possible choices, choose the correct
answer from the Correct Answer drop-down. If you don’t have your hand on the
mouse, you can select the correct answer by pressing the Tab key to highlight
the drop-down and then pressing the letter of the correct answer (A through E).

The choices you provide will be shown on TurningPoint, HTML, and plain text
output formats, but the PDF/paper quiz format will show only the question. (This
decision was made because it’s not much more difficult to hand-grade quizzes
that have fill-in-the-blanks answers as opposed to multiple-choice answers, and
they test knowledge more effectively.)

If you would prefer to always place the correct answer in box A and then
randomize the answers after you’re finished adding answers, you may wish to set
the “auto-select answer A” option in the preferences. If you choose this option,
be careful if you create questions with a choice such as “all of the above” –
the randomize option is not smart enough to deal with these and will happily
make “all of the above” the first choice. On the other hand, if you attempt to
close the dialog without randomizing the answers, you will be warned that most
of the answer choices seem to be “A”, so you don’t have to worry about
accidentally giving a quiz where all the questions have the same answer.

### The question list

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
* *Answers A-E*, in order. If you only want to use choices A through C and
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


# The Students window

The Students window shows information about the students in your classes. You
can choose what class you’re editing students for with the Class drop-down at
the top of the window. In general, the information in the students window
should be identical to the Participant List in TurningPoint. (If you are not
using TurningPoint, there is no need to put your students into the students
window unless you want to.)

## Table columns

There are several important pieces of information about each of your students:

* **The student’s name**, so you don’t have to call your student `9a2e3b`
  everywhere in the program.
* The student’s **TurningPoint ID** (*TP ID*, *User ID*). This value is used to
  match the student in CQM with the participant and results in TurningPoint.
  This value must be unique for each student, and it must match the ID listed
  in TurningPoint for that student, or CQM will be unable to import results
  (or, worse, some students will have their scores swapped). Numbers starting
  with 1 are often convenient IDs, but any value can be used as long as it is
  unique and matches the one in TurningPoint.
* The student’s **device ID** (*TP Device*). This value should match the device
  ID printed on the back of the remote the student normally uses. This field is
  not required in CQM; it’s fine to use any method supported by TurningPoint
  for matching participants to remotes, as long as TurningPoint has the right
  name associated with the right remote (and the TP ID in TurningPoint matches
  the ID in CQM).
* The student’s **email address**. This is used to email the student’s results.
  If you don’t plan to email results, this field is not necessary.

## Editing students

To edit entries in the table, double-click on the cell you want to edit, or
select it and press **F2**. Once you are editing a cell, you can use the
**Tab** key to proceed to the next cell.

If you need to add or delete a lot of entries at once, you can turn on the
**Fast edit** option in the upper-right corner. When fast edit is enabled,
pressing Enter after you’ve finished entering a row will add a new row, and
clicking the Delete button will delete the row without confirmation.

## Importing and exporting

The Import and Export buttons read and write CSV data in the same format that
TurningPoint uses by default, so you can easily fill in the table in either CQM
or TurningPoint and then transfer it to the other. If you’d like to import data
from another source (such as a course management website or university
database), here is an example of the format:

<pre> 
Device ID(s),Last Name,First Name,User ID,Email
4566CE,Doe,Jane,1,janedoe@example.com
7833EE,Doe,John,2,johndoe@example.com
112345,"A Name with, Commas In It",Sir,3,sircommas@example.com 
</pre>

There are two bugs in TurningPoint at the time of this writing that can cause
issues unless you know how to deal with them:

* TurningPoint does not correctly escape fields containing quotation marks
  either on export or import, so make sure that you do not use them in student
  names, IDs, or email addresses. You’re probably unlikely to want them, but it
  will not be possible to export or import a valid file if you don’t observe
  this.
* When you import a file from CQM into TurningPoint, a new “Device ID” column
  will be incorrectly added alongside the existing one. The way to fix this is
  to delete the old one (which is all the way on the left), then drag and drop
  the new one into its place.


# The Generate Quiz window

Once you have added at least one class and some sets and questions, you can
start creating quizzes with the **Generate Quiz** window.

## New and review sets

Before trying to generate a quiz, it’s helpful to understand how sets relate to
quizzes. At any given time, in each class each of your sets is either a *new
set* or a *review set*:

* A new set has never been used on a quiz in this class; you may or may not
  want to put it on a quiz for that class in the future.
* A review set has previously been introduced on a quiz for this class; CQM
  will continue showing questions from that set on future quizzes in that
  class.

One good way to think about this is that the new sets that you choose today
will become review sets tomorrow.

A set can be a new set in some classes and a review set in other classes, since
sets are shared between classes. So we can say that in my “Fall 2015 Spanish
101” class the “Spanish Colors” set is a review set because I’ve given a quiz
on the colors earlier this semester. But in my “Fall 2015 Intro to Computer
Science” course it’s a new set, because the words for colors in Spanish have
nothing to do with computer science and so we haven’t studied (and don’t plan
to study) them.

As mentioned above, CQM keeps track of when review sets were last seen and
brings them back occasionally. It doubles the amount of time between each
showing, so if you add a new set on your first quiz, it will be a review set on
quizzes 2, 4, 8, 16, and so on. (Similarly, the new set(s) you add on the
second quiz will come back on quizzes 3, 5, 9, and 17.)

## Quiz options

When you click the Generate Quiz button in the main window, you will be
presented with some options for the quiz.

* At the top of the dialog you can select the **class** for which you want to
  generate a quiz. Selecting a different class will update the list of sets
  which have not yet been introduced in that class (*new sets*). Remember that
  any set you create can be used in any class; if the *New Sets* list changes
  when you select a different class, that's because you've introduced different
  sets in that class so far, not because some sets are “part of a different
  class” and not available in this one.

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
through the sets and questions as you would if you opened it from the main
screen.

## Previewing, saving, and rescheduling a quiz

When you’re happy with the options you’ve selected, click the **Generate**
button. CQM will give you a preview of the quiz that it's generated. You can
take a look through the questions to make sure you’re happy with the ones it’s
chosen (maybe it happened to randomly select all of the easiest or hardest
questions, or one of your two new sets got 2 questions and the other got 5, but
the first is much more important). If you’re unhappy with the selections, you
can click the **Return to Settings** button and click the **Generate** button
again to make new random selections.

When you're happy with the quiz as presented, it’s time to save the quiz to a
file for use. You can choose to save it as a *TurningPoint Quiz* (an RTF format
which can be imported into a question list in TurningPoint), a PDF (see
flibbertygibberty for info about this feature), an HTML file, or a text file.
In the case of HTML and text files, you can choose to save with or without
*answers and set names*. The easiest way to see the difference is with an
example.

With answers and set names:

<pre>
1. die Lieblingsfarbe (Namen)
    a. course
    b. pencil
    c. favorite color
    d. first name, given name
Answer: (c) favorite color
</pre>

Without answers and set names:

<pre>
1. die Tafel
	a. blackboard/whiteboard
	b. favorite color
	c. course
	d. door
</pre>

As you can see, one format is suitable for handing out as a quiz, while the
other is useful for studying a quiz later or for looking at as a teacher.

When you’re done saving the quiz in any formats you want, click the
**Reschedule** button. This will change the new set into a review set so that
it can come back later. It will also record an entry in the quiz history
window, which will allow you to look at the quiz and save it into different
formats again later.

If you decide you don’t want to use the quiz after all, you can click the
**Return to Settings** button and answer the confirmation dialog.



# Keyboard shortcuts

It should be possible to use CQM with little to no mouse input once you become
familiar with it. Most buttons and fields have an underlined access character;
to activate that button or field, hold down the Alt key and press that access
character. Additionally, in the question editor, Sets dialog, and Classes
dialog, pressing Alt-L will focus the main list.

# Glossary

* set
* new set
* review set
* class
* main window
