#!/usr/bin/python
'''
    Just run test to cofirm d3trace commannd output is O.K.

    usage:
    # ./test.py

'''

import unittest
import commands

class TestD3traceFunctions(unittest.TestCase):

    def setUp(self):
        print 'setup'

    def test1(self):
        expected = open('test1_expected.js').read()
        ret = commands.getoutput('cat test1.data | ../d3trace.py')

        self.assertEqual(ret, expected.rstrip())

if __name__ == '__main__':
    unittest.main()
