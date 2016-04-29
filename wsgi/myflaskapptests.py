import os
import myflaskapp
import unittest
import tempfile
import json
from compute import introduces_liability, Trade, dates_within_range
from edgar_api import *


class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.app = myflaskapp.app.test_client()

    def test_blank(self):
        assert 1==1

    def test_introduces_liability(self):
        sampleSell = Trade(number = 1, price = 20, year = 2016, month = 01, day = 12)
        sampleBuy = Trade(number = 2, price = 10, year = 2016, month = 01, day = 10)
        test = introduces_liability(sampleBuy, sampleSell, True, True)
        assert test == True 

     # Making sure that the data being passed in is a not a list (if not, test_parse_section messes up)
    def test_section(self):
        inputFile = open('wsgi/testing/edgarTestingFile.txt', 'r+')
        tree = parse_section_4(inputFile)
        assert not (isinstance(tree, list))

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


    def test_get_all_URLs_from_idx(self):
        inputFile = open('wsgi/testing/edgarTestIndex.txt', 'r+')
        edgarFileURLs = get_all_URLs_from_idx(inputFile, ['4'])
        assert edgarFileURLs[0] == 'edgar/data/1000180/0001242648-07-000020.txt'
        assert edgarFileURLs[9] == 'edgar/data/1000180/0001242648-07-000029.txt'
    
    def test_get_URLs_for_CIK(self):
        inputFile = open('wsgi/testing/edgarTestIndex.txt', 'r+')
        edgarFileURLs = get_URLs_for_CIK(inputFile, 1000180, ['4'])
        assert edgarFileURLs[0] == 'edgar/data/1000180/0001242648-07-000020.txt'
        assert edgarFileURLs[9] == 'edgar/data/1000180/0001242648-07-000029.txt'

    # Making sure that the data being passed in is a list (if not, test_pull_trades messes up)
    def test_trades(self):
        inputFile = open('wsgi/testing/computetest.txt', 'r+')
        data  = json.load(inputFile)
        assert isinstance(data, list)

     # This test can be flaky depending on the connection to the SEC database
    def test_pull_trades(self):
        jsonData = json.dumps({ "startYear": 2007, "startMonth": 1, "endYear": 2007, "endMonth": 3, "cik": 1000180 })
        rv = self.app.post('/pullSEC', content_type= 'application/json', data = jsonData)
        data = json.loads(rv.data)
        assert data['sells'][0] == {"day": 11,"month": 1,"number": 2000,"price": 44.1, "year": 2007, "securityTitle":"Common Stock", "directOrIndirectOwnership" : "D", "filingURL" : "http://www.sec.gov/Archives/edgar/data/1000180/000124264807000001/0001242648-07-000001-index.htm"}

    # # Testing the ability to pull files locally
    def test_pull_index_local(self):
        # Give an ftp that is bad.  This will cause a failure if it doesn't pull the correct file
        year = 2008
        quarter = 1
        indexType = 'master'
        fileLoc = 'edgar/full-index/' + str(year) + '/QTR' + str(quarter) + '/' + indexType + '.gz'
        assert os.path.isfile("wsgi/tempFiles/"+fileLoc) #Be sure to include this file in this location for this test to pass
        pull_edgar_file("bad_ftp",fileLoc)

    # Testing if root data is empty
    def test_if_empty(self):
        rv = self.app.get('/')
        assert "" in rv.data

if __name__ == '__main__':
    unittest.main()
