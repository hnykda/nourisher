'''
Created on Dec 19, 2014

@author: dan
'''
import unittest

from nourisher.nourisher import  Nourisher
from urllib.error import URLError
testingUrl = 'http://www.huffingtonpost.com/news/authors/feed/'
fakeBadUrl = 'http://nonexistingurljustfortests.badass'

gn = Nourisher( testingUrl )

class TestNourisher( unittest.TestCase ):

    def test_check_response( self ):
        urlTrue = gn.check_response( testingUrl )
        self.assertTrue( urlTrue )

    def test_init( self ):
        iniTes = gn.origFeedUrl

        self.assertEqual( iniTes, testingUrl )
        self.assertRaises( Exception, Nourisher, fakeBadUrl )



if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
