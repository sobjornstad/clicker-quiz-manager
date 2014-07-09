import sqlite3 as sqlite

connection = None
cursor = None

def connect(fname):
    global connection, cursor
    connection = sqlite.connect(fname)
    cursor = connection.cursor()
