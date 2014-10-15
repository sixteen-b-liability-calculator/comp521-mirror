import os
import myflaskapp
import unittest
import tempfile

class FlaskrTestCase(unittest.TestCase):


    def test_empty_db(self):
        rv = self.get('/')
        assert 'No entries here so far' in rv.data

if __name__ == '__main__':
    unittest.main()