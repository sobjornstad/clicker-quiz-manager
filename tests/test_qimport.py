import db.questions
import db.sets
import db.qimport
import utils

class ImportTests(utils.DbTestCase):
    def testProperImport(self):
        ourSt = db.sets.Set("Maud's Set", 1)

        fname = 'tests/resources/test_qimport.txt'
        importer = db.qimport.Importer(fname, ourSt)
        importer.txtImport()

        # test that they got put there properly
        ql = db.questions.getBySet(ourSt)
        assert len(ql) == 2
        q1, q2 = ql
        assert q1.getQuestion() == "What species am I a member of?"
        # following also tests that stripping unused answers is working properly
        assert q1.getAnswersList() == ["human", "dwarf", "elf", "troll"]
        assert q1.getCorrectAnswer() == 'c'
        assert q1.getOrder() == 1
        assert q1.getSet() == ourSt

    def testImproperImport(self):
        # import with the wrong number of fields and an invalid answer choice
        ourSt = db.sets.Set("Maud's Set", 1)
        fname = 'tests/resources/test_qimport_invalid_file.txt'
        importer = db.qimport.Importer(fname, ourSt)
        errs = importer.txtImport()


if __name__ == "__main__":
    unittest.main()
