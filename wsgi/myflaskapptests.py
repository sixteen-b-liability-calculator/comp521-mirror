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

    	expectedBuy = dict(price = 44.10, month = 1, number = 2000, day = 11, year = 2007)
    	expectedSell = dict(price= 34.585, month= 1, number= 10000, day= 11, year= 2007)

        inputFile = open('testing/edgarTestingFile.txt', 'r+')
        tree = parse_section_4(inputFile)
        assert tree.getroot().tag == 'ownershipDocument'
        trades = return_trade_information_from_xml(tree)

        assert trades[0][0] == expectedBuy
        assert trades[1][0] == expectedSell  

    def test_parse_idx(self):

    	inputFile = open('testing/edgarTestIndex.txt', 'r+')
    	edgarFileURLs = parse_idx(inputFile, 1000180, ['4'])
    	assert edgarFileURLs[0] == 'edgar/data/1000180/0001242648-07-000020.txt'
    	assert edgarFileURLs[9] == 'edgar/data/1000180/0001242648-07-000029.txt'

    # This test can be flaky depending on the connection to the SEC database
    def test_pull_trades(self):
        jsonData = json.dumps({ "year": 2007, "quarter": 1, "cik": 1000180 })
        rv = self.app.post('/pullSEC', content_type= 'application/json', data = jsonData)
        data = json.loads(rv.get_data())

        assert data['buys'][0] == {"day": 11,"month": 1,"number": 2000,"price": 44.1, "year": 2007}



if __name__ == '__main__':
    unittest.main()