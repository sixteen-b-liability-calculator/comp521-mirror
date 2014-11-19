from dateFunctions import *
import unittest

class FlaskrTestCase(unittest.TestCase):

    def test_month2quarter(self):
        assert month2quarter(3) == 1
        assert month2quarter(4) == 2
        assert month2quarter(7) == 3

    def test_isStartBeforeEnd(self):
        assert isStartBeforeEnd(2007, 1, 2008,2) == ""

if __name__ == '__main__':
    unittest.main()