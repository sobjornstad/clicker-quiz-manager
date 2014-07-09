import database as d

class Set(object):
    def __init__(self, name, num, sid=None):
        self._name = name
        self._num = num
        self._sid = sid
        self.dump()

    def getName(self):
        return self._name
    def getNum(self):
        return self._num
    def getSid(self):
        return self._sid

    def setName(self, name):
        self._name = name
        self.dump()
    def setNum(self, num):
        self._num = num
        self.dump()
    # you cannot reset the sid of an existing set, thus no function is provided

    def dump(self):
        if self._sid:
            # exists already
            d.cursor.execute('UPDATE sets SET name=?, num=? WHERE sid=?',
                    (self._name, self._num, self._sid))
        else:
            # new set, not in db
            d.cursor.execute('INSERT INTO sets VALUES (null, ?, ?)',
                    (self._name, self._num))
            d.cursor.execute('SELECT sid FROM sets WHERE name=? AND num=?',
                    (self._name, self._num))
            self._sid = d.cursor.fetchall()[0][0]

        # at some point we will want to eliminate this for performance reasons;
        # just leaving it here to make sure things are consistent for now
        d.connection.commit()

def getSetBySid(sid):
    """Return a Set from the db when given the sid. Return None if it doesn't
    exist."""

    d.cursor.execute('SELECT name, num FROM sets WHERE sid=?', (sid,))
    name, num = d.cursor.fetchall()[0]
    if name and num:
        return Set(name, num, sid)
    else:
        return None
