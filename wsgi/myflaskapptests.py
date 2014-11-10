import os
import myflaskapp
import unittest
import tempfile
from edgar_api import *
class FlaskrTestCase(unittest.TestCase):

    def test_blank(self):
        assert 1==1

    def test_parse_section_4(self):

    	expectedBuy = dict(price = 44.10, month = 1, number = 2000, day = 11, year = 2007)
    	expectedSell = dict(price= 34.585, month= 1, number= 10000, day= 11, year= 2007)

        inputFile = open('edgarTestingFile.txt', 'r+')
        tree = parse_section_4(inputFile)
        assert tree.getroot().tag == 'ownershipDocument'
        trades = return_trade_information_from_xml(tree)

        assert trades[0][0] == expectedBuy
        assert trades[1][0] == expectedSell  


if __name__ == '__main__':
    unittest.main()
