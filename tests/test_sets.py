import utils
import db.sets

class SetTests(utils.DbTestCase):
    def testDbWriteRead(self):
        # create a set in db; make sure it has a sid
        s = db.sets.Set("Maud's Questions", 3)
        assert s.getSid() is not None, "sid unset after dump"

        # update the set; sid should not change
        savedSid = s.getSid()
        s.setName("Maud's Question Set")
        assert savedSid == s.getSid(), "sid changed after update"

        # pull the set back in and make sure it's the same
        s2 = db.sets.findSet(sid=s.getSid())
        assert s2 is not None, "set did not exist in db"
        assert s.getName() == s2.getName()
        assert s.getNum()== s2.getNum()

    def testGets(self):
        # create two sets
        s = db.sets.Set("First Set", 1)
        s2 = db.sets.Set("Second Set", 2)

        # pull list of sets and make sure it contains what we added
        sl = db.sets.getAllSets()
        assert len(sl) == 2, sl
        assert sl[0] == s and sl[1] == s2

        #TODO: add checks based on number

        # get class set by name
        sByName = db.sets.findSet(name="Second Set")
        assert sByName == s2

        # by sid
        sBySid = db.sets.findSet(sid=s.getSid())
        assert sBySid == s

        # by num
        sByNum = db.sets.findSet(sid=s.getNum())
        assert sByNum == s

    def testNonexistentGets(self):
        # try getting things that don't exist
        assert db.sets.findSet(name="tulgey") == None
        assert db.sets.findSet(sid=9000) == None
        assert db.sets.findSet(num=9000) == None

    def testDupeCheck(self):
        # create a set in db to check against
        s = db.sets.Set("First Set", 1)

        # name check
        assert db.sets.isDupe(name="First Set")
        assert not db.sets.isDupe(name="Second Set")

        # sid check
        sid = db.sets.findSet(name="First Set").getSid()
        assert db.sets.isDupe(sid=sid)
        assert not db.sets.isDupe(sid=9000)

        # num check
        num = db.sets.findSet(name="First Set").getNum()
        assert db.sets.isDupe(num=num)
        assert not db.sets.isDupe(num=9000)

    def testDelete(self):
        s = db.sets.Set("Doomed Set", 1)
        assert db.sets.isDupe(num=1)
        s.delete()
        assert not db.sets.isDupe(num=1)

    def testSwap(self):
        s = db.sets.Set("First Set", 1)
        s2 = db.sets.Set("Second Set", 2)

        db.sets.swapRows(s, s2)
        assert s.getNum() == 2, s.getNum()
        assert s2.getNum() == 1
