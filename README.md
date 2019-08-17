DESCRIPTION
-----------

Clicker Quiz Manager is a tool I wrote some years ago
for creating and tracking students' results on quizzes administered
with remote-control "clickers" like those offered by Turning Technologies
(specifically, this tool integrates with their TurningPoint software).

The tool never went into production for the client I wrote it for,
and I have not even attempted to use the software for 4 years at this point,
so there are no guarantees it works perfectly.
However, I wanted to get it out here in the event it's useful to somebody;
at the least, it might be a good starting point.

Feel free to email me with questions (`contact@sorenbjornstad.com`),
but I will not be doing further development or debugging on CQM.


RUNNING
-------

To run the Clicker Quiz Manager, double-click on the 'runcqm' file. If you're
running Windows, you can first rename it to 'runcqm.py' so that the Python
interpreter will run it for you.

On first run, you need to cancel the database selection, then choose File ->
New Database. I'm going to fix this up at some point.

For more information on using Clicker Quiz Manager, look at the user manual in
the docs/ directory.


DEPENDENCIES
------------

- Python 2.7
- PyQt 4
- sqlite3

Python packages:
- BeautifulSoup 4 (pip install beautifulsoup4)
- PyRTF (packaged in the thirdparty/ directory)
- rtfunicode (packaged in the thirdparty/ directory)

Additionally, to use the printed quiz function, you need to have LaTeX
installed, with a few packages: fontspec, xunicode, geometry, setspace,
titlesec, microtype, ebgaramond, ifluatex, ifxetex. The files need to be
compiled with the XeTeX engine to display correctly.

If you can't install those packages or want to render the output in a different
manner, it's possible to edit the LaTeX header in db/resources.

For development, you will also need the following dependencies:
- pyuic4 (to rebuild modified Qt Designer files)
- the development headers for PyQt 4
