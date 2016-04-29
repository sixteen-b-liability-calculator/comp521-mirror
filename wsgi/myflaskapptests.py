import os
import myflaskapp
import unittest
import tempfile
import json
from edgar_api import *
class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.app = myflaskapp.app.test_client()

    def test_blank(self):
        assert 1==1

    def test_parse_section_4(self):

    	expectedSell = dict(price = 44.10, month = 1, number = 2000, day = 11, year = 2007,
                           securityTitle="Common Stock", directOrIndirectOwnership="D", filingURL ="ftp://ftp.sec.gov/")
    	expectedBuy = dict(price= 34.585, month= 1, number= 10000, day= 11, year= 2007,
                            securityTitle="Common Stock", directOrIndirectOwnership="D", filingURL ="ftp://ftp.sec.gov/")

        inputFile = open('wsgi/testing/edgarTestingFile.txt', 'r+')
        tree = parse_section_4(inputFile)
        assert tree.getroot().tag == 'ownershipDocument'
        trades = return_trade_information_from_xml(tree,"")
        assert trades[0][0] == expectedBuy
        assert trades[1][0] == expectedSell  

    # parse_idx ws not used
        
    # def test_parse_idx(self):

    # 	inputFile = open('wsgi/testing/edgarTestIndex.txt', 'r+')
    # 	edgarFileURLs = parse_idx(inputFile, 1000180, ['4'])
    # 	assert edgarFileURLs[0] == 'edgar/data/1000180/0001242648-07-000020.txt'
    # 	assert edgarFileURLs[9] == 'edgar/data/1000180/0001242648-07-000029.txt'

    # This test can be flaky depending on the connection to the SEC database

    def test_pull_trades(self):
        jsonData = json.dumps({ "startYear": 2007, "startMonth": 1, "endYear": 2007, "endMonth": 3, "cik": 1000180 })
        rv = self.app.post('/pullSEC', content_type= 'application/json', data = jsonData)
        data = json.loads(rv.get_data())
        assert data['sells'][0] == {"day": 11,"month": 1,"number": 2000,"price": 44.1, "year": 2007, "securityTitle":"Common Stock", "directOrIndirectOwnership" : "D", "filingURL" : "http://www.sec.gov/Archives/edgar/data/1000180/000124264807000001/0001242648-07-000001-index.htm"}

    # def test_pull_daily_filings(self):
    #     d = {'dataString': '01/01/2016'}
    #     jsonData = json.dumps(d)
    #     rv = self.app.post('/pullDailyReport', content_type = 'application/json', data = jsonData)
    #     print rv
    #     data = json.loads(rv.get_data())
    #     assert data['sells'][0] == {"day": 11, "month": 1, "number": 2000, "price": 44.1, "year": 2007, "securityTitle":"Common Stock", "directOrIndirectOwnership" : "D", "filingURL" : "http://www.sec.gov/Archives/edgar/data/1000180/000124264807000001/0001242648-07-000001-index.htm"}

    # # Testing the ability to pull files locally
    def test_pull_index_local(self):
        # Give an ftp that is bad.  This will cause a failure if it doesn't pull the correct file
        year = 2008
        quarter = 1
        indexType = 'master'
        fileLoc = 'edgar/full-index/'+str(year)+'/QTR'+str(quarter)+'/'+indexType+'.gz'
        assert os.path.isfile("wsgi/tempFiles/"+fileLoc) #Be sure to include this file in this location for this test to pass
        pull_edgar_file("bad_ftp",fileLoc)

    def test_empty_db(self):
        rv = self.app.get('/')
        assert "" in rv.data

    def test_compute(self):
        # note that the inputs must have /unique/ correct outputs or else
        # the test is meaningless
        inputFile = open('wsgi/testing/computetest.txt', 'r+')
        testDicts = json.load(inputFile)
        #print testDicts
        for test in testDicts:
            print (json.dumps(test['input']).getData())
            # computeResult = json.loads(self.app.post('/compute', content_type='application/json', data=json.dumps(test['input'])).get_data())
            # print "This is computeResult" + computeResult
            # greedyResult = json.loads(self.app.post('/greedy', content_type='application/json', data=json.dumps(test['input'])).get_data())
            # # only check the top-level keys from expected output
            # for (key, expected) in test['output_compute'].iteritems():
            #     assert computeResult.get(key) == expected
            # for (key, expected) in test['output_greedy'].iteritems():
            #     assert greedyResult.get(key) == expected

if __name__ == '__main__':
    unittest.main()
