'''
Created on Dec 21, 2014

@author: dan
'''

from nourisher.collector.maternalSite import collect_alexa
from nourisher.utiliser import push_to_db

import unittest

maternalURL = 'www.huffingtonpost.com'

class Test( unittest.TestCase ):


    def test_Alexa( self ):
        res = collect_alexa( maternalURL )
        push_to_db( res )


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
