import database as d

class Set(object):
    def __init__(self, name, num, sid=None):
        self._name = name
        self._num = num
        self._sid = sid
        self.dump()

    def __eq__(self, other):
        return self._sid == other._sid and \
                self._name == other._name and \
                self._num == other._num

    def __ne__(self, other):
        return not self.__eq__(self, other)

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

    def dump(self):
        if self._sid:
            # exists already
            d.cursor.execute('UPDATE sets SET name=?, num=? WHERE sid=?',
                    (self._name, self._num, self._sid))
        else:
            # new set, not in db
            d.cursor.execute('INSERT INTO sets VALUES (null, ?, ?)',
                    (self._name, self._num))
            self._sid = d.cursor.lastrowid

        # at some point we will want to eliminate this for performance reasons;
        # just leaving it here to make sure things are consistent for now
        d.connection.commit()

    def delete(self):
        d.cursor.execute('DELETE FROM sets WHERE sid=?', (self._sid,))
        d.connection.commit()
        # we shouldn't use this instance again of course, but the class does
        # not enforce its nonuse.


def isDupe(name=None, num=None, sid=None):
    if name and findSet(name=name):
        return True
    if num and findSet(num=num):
        return True
    if sid and findSet(sid=sid): # guarded
        return True
    return False

def findSet(sid=None, name=None, num=None):
    """
    Return a set when a sid, name, or num is given, or None if that criterion
    does not match any sets in the db. Use keyword args to specify which one
    you're providing.
    """

    vals = {'sid':sid, 'name':name, 'num':num}

    has = None
    value = None
    for i in vals.keys():
        if vals[i] is not None:
            value = vals[i]
            has = i
    if not has:
        assert False, "No criterion provided to findSet!"

    query = 'SELECT sid, name, num FROM sets WHERE %s=?' % (has)
    d.cursor.execute(query, (value,))
    try:
        sid, name, num = d.cursor.fetchall()[0]
    except IndexError:
        return None
    else:
        return Set(name, num, sid)

def getAllSets():
    """Return a list of all sets in the database, ordered by their num field
    for insertion into a correctly ordered list."""

    d.cursor.execute('SELECT sid FROM sets ORDER BY num')
    return [findSet(sid=i[0]) for i in d.cursor.fetchall()]
