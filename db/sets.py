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
            self._sid = d.cursor.lastrowid

        # at some point we will want to eliminate this for performance reasons;
        # just leaving it here to make sure things are consistent for now
        d.connection.commit()

def isDupe(name=None, num=None, sid=None):
    if name and getSetByName(name):
        return True
    if num and getSetByNumber(num):
        return True
    if sid and getSetBySid(sid): # guarded
        return True
    return False

#TODO: Make these use an umbrella function
def getSetBySid(sid):
    """Return a Set from the db when given the sid. Return None if it doesn't
    exist."""

    d.cursor.execute('SELECT name, num FROM sets WHERE sid=?', (sid,))
    try:
        name, num = d.cursor.fetchall()[0]
    except IndexError:
        return None
    else:
        return Set(name, num, sid)

def getSetByName(name):
    """Return a Set from the db when given the name. Return None if it doesn't
    exist."""

    d.cursor.execute('SELECT sid, num FROM sets WHERE name=?', (name,))
    try:
        sid, num = d.cursor.fetchall()[0]
    except IndexError:
        return None
    else:
        return Set(name, num, sid)

def getSetByNumber(num):
    """Return a Set from the db when given the number. Return None if it doesn't
    exist."""

    d.cursor.execute('SELECT sid, name FROM sets WHERE num=?', (num,))
    try:
        sid, name = d.cursor.fetchall()[0]
    except IndexError:
        return None
    else:
        return Set(name, num, sid)

def getAllSets():
    """Return a list of all sets in the database."""

    d.cursor.execute('SELECT sid FROM sets')
    return [getSetBySid(i[0]) for i in d.cursor.fetchall()]

def deleteSet(name):
    name = str(name) # dumb QStrings
    cid = getSetByName(name).getSid()
    #TODO: When we have questions, we need to delete those
    d.cursor.execute('DELETE FROM sets WHERE sid=?', (sid,))
    d.connection.commit()
    #TODO: Cause the class to raise some kind of error if we try to use it
