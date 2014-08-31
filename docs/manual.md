Introduction
============

This is the manual for the **Clicker Quiz Manager**, version 1.0.0. The application
allows you to manage classes, sets of questions, and review history in order to
generate daily clicker quizzes for your students.


Creating a database
===================

Before you can use CQM, you must create a new database. Currently this must be
done manually by running the script ```db/tools/create_database.py```. On
Windows, if you have Python installed, you should be able to run this by
double-clicking on it; on other operating systems, run the script using
whatever method is usual.

You will be prompted for a filename; after entering it and pressing Enter, the
script will place a file of that name in your current directory and then exit.
If you double-clicked on the script from within the
```db/tools/create_database``` folder, the file will be in that folder.
Otherwise, if you ran it from a different directory in your terminal, it will
be in the directory you ran the script from.

Once the file is created, you may move it anywhere you like.


Starting the application
========================

To run CQM, double-click on the ```runcqm``` file in the main program folder.
(If you are using Windows, you will first need to rename the file to
```runcqm.py``` so that the computer will know to use Python to run it.) In the
resulting file dialog, select the database file that you created in the
**Creating a database** section. After clicking OK, the main program window
should open.

CQM automatically saves your changes as you go along, so there is no need to
save manually. When you are done working with CQM for the moment, simply quit
the program.

If you want to use a different database file, you can quit the program and
reopen it. Generally, however, there is no reason to maintain multiple database
files unless you have two "universes" of classes which you will never want to
share any information between: one database file can manage multiple classes
and any number of questions.


Working with classes
====================

You probably want to keep a separate review history for each class that you
teach. In this way, you can introduce different questions or the same questions
in different orders to each of the classes, and you can reuse the sets of
questions that you've built up from year to year. For this purpose, CQM
provides the appropriately named **classes**. You can edit your classes by
clicking the *classes* button in the main window.

The Classes window is fairly straightforward. At the top is a list of all the
classes you currently have, arranged in alphabetical order; at the bottom you
can add new classes and rename or delete existing classes. Deleting a class
will never touch any of your questions, but it will permanently delete any
review history that you have for that class, so be careful.

You should not create generalized classes like "History" or "German" – you
would end up in trouble when you taught German for a second semester, since
trying to reuse that class would mean that you would start with all the sets
that you used last year treated as already introduced. Instead, you should name
them something like "History Fall 2014." Since classes are listed throughout the
program in alphabetical order, you will probably obtain a more useful sort by
naming with the time first, so "Fall 2014 - History". This way history classes
in future semesters will be grouped along with your first ones, if you choose to
keep them around for future reference.

Any class may use any questions that you have in your database, so creating
classes does not need to divide up your questions in any way.


Working with sets
=================

A *set* or *question set* is a group of questions that will be introduced on a
certain quiz. For instance, a set might contain questions about the accusative
case in German.

The sets dialog is very similar to the classes dialog, with the addition of
"move up" and "move down" buttons since you may want to group your sets in ways
other than alphabetical order; perhaps you want to put similar topics together.

Deleting a set will delete all of its questions, but will not touch your review
history. To be honest, I'm completely uncertain as to what will happen if you
delete a set that has review history, though, so don't do that yet.


Adding and editing questions
============================

Once you have some sets and classes, it's time to start adding actual questions.
You do this by selecting the set you want to edit and clicking the edit button,
or simply by double-clicking the set's name in the list.

The question editor has two main parts. On the left is a list of all the
questions that the set currently has, along with some buttons to edit the list.
On the right is a display of the content of the currently selected question.
When you create a new question or begin to edit an existing one, the question
list is disabled until you save or discard the changes to the question you're
editing, at which point you can select other questions once again. When you
first open a new set, a new question is automatically created and you are
dropped into editing mode, since there is no point in editing the question list
until you have at least one question.

The interface elements on the selected question side are as follows:

* **Question**: This is the content of the quiz question you will be asking your
  students.
* **Difficulty**: This spinner does not do anything in version 1.0.0. You can
  set it to whatever you like, but it will have no effect, and what you select
  will not be saved after you switch to another question and come back.
* **Answers A-E**: You may fill two to five of these boxes, which will
  correspond to multiple-choice answer options on the final quiz. The choices
  will not be randomized, so you will want to place the correct answer in
  different boxes; a future version will probably have a randomize option.
* **Correct Answer**: Indicate which answer in the above boxes is the correct
  one. To speed things up, you can press Alt-A to select this combo box and then
  just type the letter (A-E) that corresponds to the correct answer choice.
* **Save Changes**: Clicking this button creates the new question or saves the
  changes you've made to an existing one. If you try to save but haven't created
  a valid question (for instance, you've provided only choices A and E, or you
  left the *question* box blank), CQM will refuse to save and will tell you what
  the problem is.
* **Discard Changes**: Clicking this button cancels the new question you're
  adding or reverts to the previous version of an existing one. You cannot
  choose this option if a question doesn't exist yet.

The options on the question list side are pretty self-explanatory. **Export** is
not implemented in version 1.0.0; **Import** will allow you to import questions
from a comma- or tab-separated text file. The file should contain the following
seven columns:

* **Question**.
* **Answers A-E**, in order. If you only want to use choices A-C and you're
  using a comma as your delimiter, simply place two extra commas after choice C
  to fill the columns with blank values.
* **The correct answer** as a lowercase or uppercase letter, A-E.

Upon clicking Import, you'll be advised if any of the rows in your file were
invalid or there were any other problems importing, and CQM will import as much
as it can.

At the very bottom of the window, there is a drop-down box labeled **Jump to
set**. You can use this to quickly switch to editing the questions of a different
set.


Generating a quiz
=================

Once you have classes, sets, and questions, you can start creating quizzes with
the **Generate Quiz** option on the main screen. Please note that in version
1.0.0 the generate quiz dialog can be sluggish at times; major performance
improvements are planned for future versions, but for now be patient and don't
worry that the program has crashed.

At the top of the dialog you can select the class for which you want to generate
a quiz. Selecting a different class will update the list of sets which have not
yet been introduced in that class (*new sets*). Remember that sets are shared
among all classes; if the *New Sets* list changes when you select a different
class, that's because you've introduced different sets in that class so far, not
because some sets are "part of a different class" and not available in this one.

For each quiz, you must select at least one new set. If you like, you can select
multiple new sets by holding down the Control or Shift keys.

At the bottom of the dialog, you choose how many new questions and how many
review questions you want to have on this quiz. New questions are drawn from the
new sets which you've selected above; the *available* display on the right tells
you how many questions total are present in those sets. If you have a
significant number of questions in those sets, you probably don't want to show
them all; if you select a smaller number than the maximum available, CQM will
pick randomly from the ones available (ensuring that at least one question from
each set is placed on the quiz).

Sets that you have already introduced (that is, ones that are not new and are
not shown anymore in the *new sets* list) are called *review sets*. In other
words, the new sets that you choose today will become review sets tomorrow. CQM
keeps track of when reviews sets were last seen and brings them back
occasionally. By default it doubles the amount of time between each showing, so
if you add a new set on your first quiz, it will be available again as a review
set on quizzes 2, 4, 8, 16, and so on. (Similarly, the new set(s) you add on the
second quiz will come back on quizzes 3, 5, 9, and 17.)

The *available* display next to the review questions spinner shows how many
total questions are in all of the sets which are up for review today. As with
new questions, if you select less than the maximum number, CQM will pick
randomly from the possible questions, always trying to place at least one
question from each review set on the quiz (of course, this is not always
possible: if there are three sets due and you only ask for two review questions,
there's nothing CQM can do to make that happen).

If you want to look at what questions are in each set in order to decide which
sets to put on the quiz, you can click the **Sets...** button and browse through
the sets and questions as you would if you opened it from the main screen.

When you've selected the right sets and the number of questions you want, click
the **Generate** button. After a moment to think, CQM will give you a preview of
the quiz that it's going to generate. Take a look through it and make sure that
you're satisfied with the questions. If you don't like the random selections it
has made, you can click **Return to Settings** and choose the **Generate** option
again to try a new random draw. If you want, you can also copy the quiz out of
this dialog box to keep a record of the questions you used.

If you're happy with the quiz as presented, you can click the **Accept Quiz**
button and save an RTF file of the quiz. When you save, CQM will reschedule the
new sets that you used as review sets and export the quiz for you. The RTF file
can then be imported into TurningPoint's "Content" section and used with the
clicker system.


Keyboard shortcuts
==================

It should be possible to use CQM with little to no mouse input once you become
familiar with it. Most buttons and fields have an underlined access character;
to activate that button or field, hold down the Alt key and press that access
character. Additionally, in the question editor, Sets dialog, and Classes
dialog, pressing Alt-L will focus the main list.
