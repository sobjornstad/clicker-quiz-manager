import sqlite3 as sqlite

connection = None
cursor = None

def connect(fname):
    global connection, cursor
    connection = sqlite.connect(fname)
    cursor = connection.cursor()

def openDbConnect(conn):
    """
    This function pulls an open connection into the database module's namespace
    for access by other parts of the program. This is useful in cases like
    running tests by creating a database in RAM (such that you can't run
    create_database separately and then reopen the connection).

    Example:
        >>> conn = db.tools.create_database.makeDatabase(':memory:')
        >>> db.database.openDbConnect(conn)
        >>> db.database.connection.commit()
    """

    global connection, cursor
    connection = conn
    cursor = connection.cursor()

def close():
    connection.close()
