import os
import myflaskapp
import compute
import unittest
import tempfile
import json
from edgar_api import *
class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.app = myflaskapp.app.test_client()

    def test_blank(self):
        assert 1==1


    # ******** TEST EDGAR_API.PY *************************************

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

<<<<<<< HEAD
    # def test_parse_idx(self):

    # 	inputFile = open('testing/edgarTestIndex.txt', 'r+')
    # 	edgarFileURLs = parse_idx(inputFile, 1000180, ['4'])
    # 	assert edgarFileURLs[0] == 'edgar/data/1000180/0001242648-07-000020.txt'
    # 	assert edgarFileURLs[9] == 'edgar/data/1000180/0001242648-07-000029.txt'
=======
    def test_parse_idx(self):
    	inputFile = open('wsgi/testing/edgarTestIndex.txt', 'r+')
    	edgarFileURLs = parse_idx(inputFile, 1000180, ['4'])
    	assert edgarFileURLs[0] == 'edgar/data/1000180/0001242648-07-000020.txt'
    	assert edgarFileURLs[9] == 'edgar/data/1000180/0001242648-07-000029.txt'
>>>>>>> 576453442b662a40ee78ea8a7fcf6b0b9d8b8b2f

    # This test can be flaky depending on the connection to the SEC database
    def test_pull_trades(self):
        jsonData = json.dumps({ "startYear": 2007, "startMonth": 1, "endYear": 2007, "endMonth": 3, "cik": 1000180 })
        rv = self.app.post('/pullSEC', content_type= 'application/json', data = jsonData)
        data = json.loads(rv.get_data())
        assert data['sells'][0] == {"day": 11,"month": 1,"number": 2000,"price": 44.1, "year": 2007, "securityTitle":"Common Stock", "directOrIndirectOwnership" : "D", "filingURL" : "http://www.sec.gov/Archives/edgar/data/1000180/000124264807000001/0001242648-07-000001-index.htm"}

    def test_pull_daily_filings(self):
        jsonData = json.dumos({"dateString": 01/01/16})
        rv = self.app.post('/ppullDailyReport', content_type = 'application/json', data = jsonData)
        data = json.loads(rv.get_data())
        assert data['sells'][0] == {"day": 11, "month": 1, "number": 2000, "price": 44.1, "year": 2007, "securityTitle":"Common Stock", "directOrIndirectOwnership" : "D", "filingURL" : "http://www.sec.gov/Archives/edgar/data/1000180/000124264807000001/0001242648-07-000001-index.htm"}

    # Testing the ability to pull files locally
    # def test_pull_index_local(self):
    #     # Give an ftp that is bad.  This will cause a failure if it doesn't pull the correct file
    #     year = 2008
    #     quarter = 1
    #     indexType = 'master'
    #     fileLoc = 'edgar/full-index/'+str(year)+'/QTR'+str(quarter)+'/'+indexType+'.gz'
    #     assert os.path.isfile("tempFiles/"+fileLoc) #Be sure to include this file in this location for this test to pass
    #     pull_edgar_file("bad_ftp",fileLoc)


    # ******** TEST COMPUTE.PY *************************************

    # Test compute LP and compute LIHO
    def test_compute(self):
        # note that the inputs must have /unique/ correct outputs or else
        # the test is meaningless
        inputFile = open('wsgi/testing/computetest.txt', 'r+')
        testDicts = json.load(inputFile)
        for test in testDicts:
            computeResult = json.loads(self.app.post('/compute', content_type='application/json', data=json.dumps(test['input'])).get_data())
            greedyResult = json.loads(self.app.post('/greedy', content_type='application/json', data=json.dumps(test['input'])).get_data())
            # only check the top-level keys from expected output
            for (key, expected) in test['output_compute'].iteritems():
                assert computeResult.get(key) == expected
            for (key, expected) in test['output_greedy'].iteritems():
                assert greedyResult.get(key) == expected

    # Test that the dates_within_range function in compute.py correctly calculates valid time period
    def test_dates_within_range(self):
        stella = bool(1)
        jammies = bool(1)
        inputFile = open('wsgi/testing/computetest.txt', 'r+')
        testDicts = json.load(inputFile)
        inputBuy = testDicts[0]['input']['buy']
        inputSell = testDicts[0]['input']['sell']
        print("inputBuy")
        print(inputBuy)
        print("inputSell")
        print(inputSell)
        for buy in inputBuy:
            for sell in inputSell:
                buyDate = ''.join(buy['day']) + "/" + ''.join(buy['month']) + ''.join(buy['year'])
                sellDate = '' + sell['day'] + "/" + sell['month'] + sell['year']
                print("buy: ")
                print(buy)
                print(buyDate)
                print("sell: ")
                print(sell)
                print(sellDate)
                # compute.dates_within_range(buy, sell, stella, jammies)
        # assert 


if __name__ == '__main__':
    unittest.main()
