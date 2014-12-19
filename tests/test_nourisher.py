'''
Created on Dec 19, 2014

@author: dan
'''
import unittest

from nourisher.nourisher import  Nourisher
testingUrl = 'http://www.huffingtonpost.com/news/authors/feed/'
fakeBadUrl = 'http://nonexistingurljustfortests.badass'

gn = Nourisher(testingUrl)
bn = Nourisher(fakeBadUrl)

class TestNourisher(unittest.TestCase):
    
    def test_check_response(self):
        urlTrue = gn.check_response(testingUrl)
        urlFalse = bn.check_response(fakeBadUrl)
        
        self.assertTrue(urlTrue)
        self.assertFalse(urlFalse)
        
    def test_init(self):
        iniTes = gn.origFeedUrl
        iniTesF = bn.origFeedUrl
        
        self.assertEqual(iniTes, testingUrl)
        self.assertEqual(iniTesF, fakeBadUrl)
        
    def test_collect_all(self):
        colF = bn.collect_all()
        
        self.assertEqual(colF, None)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()