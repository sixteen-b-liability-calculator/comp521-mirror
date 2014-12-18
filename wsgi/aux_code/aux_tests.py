from dateFunctions import *
from createCSV import *
import unittest

class FlaskrTestCase(unittest.TestCase):

    def test_month2quarter(self):
        assert month2quarter(3) == 1
        assert month2quarter(4) == 2
        assert month2quarter(7) == 3

    def test_isStartBeforeEnd(self):
        assert isStartBeforeEnd(2007, 1, 2008,2) == ""

    # Basic Test
    def test_csv2trade_good(self):
        
        initString = """2012/12/2, 1, 2, b
                        2014/11/3, 2, 3, b"""
        trades = csv2trade(initString)

        assert (type(trades) == dict)
        buys = trades["buys"]
        sells = trades["sells"]
        trade1 = buys[0]
        trade2 = buys[1]

        assert (trade1['price'] == '1')
        assert (trade1['number'] == '2')
        assert (trade2['month'] == '11')

    # Ignores the first line if it's text
    def test_csv2trade_withTitleLine(self):
        initString = """Date, price, number, buyOrSell
                        2012/12/2, 1, 2, b
                        2014/11/3, 2, 3, b"""
        trades = csv2trade(initString)

        assert (type(trades) == dict)
        buys = trades["buys"]
        sells = trades["sells"]
        trade1 = buys[0]
        trade2 = buys[1]


        assert (trade1['price'] == '1')
        assert (trade1['number'] == '2')
        assert (trade2['month'] == '11')        

    # Ignores lines that have an invalid date on the first line
    def test_csv2trade_invalidDateFormat_dateIssue(self):
        initString = """Date, price, number
                        2012/12, 1, 2, b
                        2014/11/3, 2, 3, b"""
        trades = csv2trade(initString)

        assert (type(trades) == dict)
        buys = trades["buys"]
        assert (len(buys) == 1)
        sells = trades["sells"]
        assert (len(sells) == 0)
        trade2 = buys[0]


        assert (trade2['day'] == '3')
        assert (trade2['year'] == '2014')
        assert (trade2['month'] == '11')        

    # Ignores lines that don't have at least 3 values to read in a line.  
    def test_csv2trade_invalidCsvFormat(self):
        initString = """Date, price, number
                        2012/12/1, 2, b
                        2014/11/3,   2,        3, b"""
        trades = csv2trade(initString)

        assert (type(trades) == dict)
        buys = trades["buys"]
        assert (len(buys) == 1)
        sells = trades["sells"]
        assert (len(sells) == 0)
        trade2 = buys[0]

        assert (trade2['day'] == '3')
        assert (trade2['year'] == '2014')
        assert (trade2['month'] == '11')

if __name__ == '__main__':
    unittest.main()