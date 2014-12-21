'''
Created on Dec 21, 2014

@author: dan
'''

from nourisher.collector.maternalSite import collect_alexa, collect_websiteout, \
    collect_urlm, maternal_that_all
from nourisher.utiliser import push_to_db, get_from_db

import unittest

maternalURL = 'www.huffingtonpost.com'

class Test( unittest.TestCase ):
    def test_Alexa( self ):
        res = collect_alexa( maternalURL )
        insId = push_to_db( res )

        retr = get_from_db( insId )

        self.assertEqual( res['link'], retr['link'] )

    def test_Websiteout( self ):
        res = collect_websiteout( maternalURL )
        insId = push_to_db( res )

        retr = get_from_db( insId )

        self.assertEqual( res['link'], retr['link'] )

    def test_Urlm( self ):
        res = collect_urlm( maternalURL )
        insId = push_to_db( res )

        retr = get_from_db( insId )

        self.assertEqual( res, retr )

    def test_maternal_that_all( self ):
        res = maternal_that_all( maternalURL )
        insId = push_to_db( res )

        retr = get_from_db( insId )

        self.assertEqual( res["alexa"]["link"], retr['alexa']["link"] )
        self.assertEqual( res["websiteout"]["link"], retr["websiteout"]["link"] )
        self.assertEqual( res["urlm"]["link"], retr["urlm"]["link"] )


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
