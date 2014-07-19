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
        s2 = db.sets.getSetBySid(s.getSid())
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
        sByName = db.sets.getSetByName("Second Set")
        assert sByName == s2

    def testNonexistentGets(self):
        # try getting things that don't exist
        assert db.sets.getSetByName("tulgey") == None
        assert db.sets.getSetBySid(9000) == None

    def testDupeCheck(self):
        # create a set in db to check against
        s = db.sets.Set("First Set", 1)

        # name check
        assert db.sets.isDupe(name="First Set")
        assert not db.sets.isDupe(name="Second Set")

        # sid check
        sid = db.sets.getSetByName("First Set").getSid()
        assert db.sets.isDupe(sid=sid)
        assert not db.sets.isDupe(sid=9000)

        # num check
        num = db.sets.getSetByName("First Set").getNum()
        assert db.sets.isDupe(num=num)
        assert not db.sets.isDupe(num=9000)
