'''
Created on Dec 22, 2014

@author: dan
'''
import unittest

testingUrl = 'http://www.huffingtonpost.com/news/authors/feed/'
# testingUrl = 'http://www.irinnews.org/top10.xml'
# testingUrl = 'http://css-tricks.com/frosting-glass-css-filters/feed/'

from nourisher.utiliser import push_to_db, get_from_db
from nourisher.collector.feeder import feed_that_all

class Test( unittest.TestCase ):

    def test_Feeder( self ):
        """Pass data for functions from feeder, not just the end function"""
        feed_that_all( testingUrl )
        pass

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
