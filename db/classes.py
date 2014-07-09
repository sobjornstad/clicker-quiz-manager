import database as d

class Class(object):
    def __init__(self, name, cid=None):
        self._name = name
        self._cid = cid
        self.dump()

    def __eq__(self, other):
        return self._cid == other._cid and self._name == other._name

    def __ne__(self, other):
        return not self.__eq__(self, other)

    def getName(self):
        return self._name
    def getCid(self):
        return self._cid
    def setName(self, name):
        self._name = name
        self.dump()

    def dump(self):
        if self._cid:
            # exists already
            d.cursor.execute('UPDATE classes SET name=? WHERE cid=?',
                    (self._name, self._cid))
        else:
            # new set, not in db
            d.cursor.execute('INSERT INTO classes (name) VALUES (?)',
                    (self._name,))
            self._cid = d.cursor.lastrowid

        # at some point we will want to eliminate this for performance reasons;
        # just leaving it here to make sure things are consistent for now
        d.connection.commit()

def getClassByCid(cid):
    """Return a Class from the db when given the cid. Return None if it doesn't
    exist."""

    d.cursor.execute('SELECT name FROM classes WHERE cid=?', (cid,))
    name = d.cursor.fetchall()[0][0]
    if name and cid:
        return Class(name, cid)
    else:
        return None
