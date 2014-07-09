import database as d

class Set(object):
    def __init__(self, name, num, sid=None):
        self.name = name
        self.num = num
        self.sid = sid

    def dump(self):
        if self.sid:
            # exists already
            d.cursor.execute('UPDATE sets SET name=?, num=? WHERE sid=?',
                    (self.name, self.num, self.sid))
        else:
            # new set, not in db
            d.cursor.execute('INSERT INTO sets VALUES (null, ?, ?)',
                    (self.name, self.num))
            d.cursor.execute('SELECT sid FROM sets WHERE name=? AND num=?',
                    (self.name, self.num))
            self.sid = d.cursor.fetchall()[0][0]

        d.connection.commit()

def setBySid(sid):
    """Return a Set from the db when given the sid. Return None if it doesn't
    exist."""

    d.cursor.execute('SELECT name, num FROM sets WHERE sid=?', (sid,))
    name, num = d.cursor.fetchall()[0]
    if name and num:
        return Set(name, num, sid)
    else:
        return None
