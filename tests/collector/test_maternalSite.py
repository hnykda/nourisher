'''
Created on Dec 21, 2014

@author: dan
'''

from nourisher.collector.maternalSite import maternal_that_all
from nourisher.collector.maternalSite import collect_alexa, collect_ranks, collect_urlm, collect_websiteout
from nourisher.utiliser import push_to_db, get_from_db

import unittest
from unittest.suite import TestSuite

# maternalURL = 'www.huffingtonpost.com'
BadmaternalURL = 'www.asdsgsdfgdfgdfgdfgxxsa.com'
maternalURL = "www.scoop.it"

class Test( unittest.TestCase ):
#     def test_Alexa( self ):
#         res = collect_alexa( maternalURL )
#         insId = push_to_db( res )
#
#         retr = get_from_db( insId )
#
#         self.maxDiff = None
#         self.assertDictEqual( res, retr )
#         self.assertRaises( RuntimeError, collect_alexa, BadmaternalURL )

    def test_Websiteout( self ):
        res = collect_websiteout( maternalURL )
        insId = push_to_db( res )

        retr = get_from_db( insId )

        self.maxDiff = None
        self.assertDictEqual( res, retr )
        self.assertRaises( RuntimeError, collect_websiteout, BadmaternalURL )

#     def test_Urlm( self ):
#         res = collect_urlm( maternalURL )
#         insId = push_to_db( res )
#
#         retr = get_from_db( insId )
#
#         self.maxDiff = None
#         self.assertDictEqual( res, retr )
#         self.assertRaises( RuntimeError, collect_urlm, BadmaternalURL )
#
#     def test_Ranks( self ):
#         res = collect_ranks( maternalURL )
#         insId = push_to_db( res )
#
#         retr = get_from_db( insId )
#         self.maxDiff = None
#         self.assertDictEqual( res, retr )
        # self.assertRaises( RuntimeError, collect_ranks, BadmaternalURL )


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main( verbose = 2 )
