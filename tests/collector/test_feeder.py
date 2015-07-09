'''
Created on Dec 22, 2014

@author: dan
'''
import unittest

urls = ['http://www.huffingtonpost.com/news/authors/feed/',
            'http://www.irinnews.org/top10.xml',
            'http://css-tricks.com/frosting-glass-css-filters/feed/'
            ]

from nourisher.collector.feeder import feed_that_all

class Test( unittest.TestCase ):

    def test_Feeder( self ):
        for url in urls:
            feed_that_all( url )

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
