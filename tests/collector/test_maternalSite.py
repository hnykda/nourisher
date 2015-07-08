'''
Created on Dec 21, 2014

@author: dan
'''

from nourisher.collector.maternalSite import maternal_that_all
from nourisher.collector.maternalSite import Urlm, Alexa, Websiteout, RankerDist
from nourisher.utiliser import push_to_db, get_from_db, get_webdriver

import unittest
from unittest.suite import TestSuite

# maternalURL = 'www.huffingtonpost.com'
BadmaternalURL = 'www.asdsgsdfgdfgdfgdfgxxsa.com'
maternalURL = "www.ihned.cz"
webdriver = get_webdriver()
class Test( unittest.TestCase ):

    # def test_Urlm( self ):
    #    urlm = Urlm(maternalURL, "www.urlm.co", '//*[@id="url"]', webdriver)
    #    urlm.collect_that_all()
    #
    # def test_Alexa( self ):
    #     alexa = Alexa(maternalURL, "www.alexa.com", '//*[@id="search-bar"]/form/input', webdriver)
    #     alexa.collect_that_all()
    #
    # def test_Ranks( self ):
    #     ranks = RankerDist(maternalURL, "www.google.com", '//*[@id="lst-ib"]', webdriver)
    #     ranks.collect_that_all()

    # def test_Webout( self ):
    #     webout = Websiteout(maternalURL,"www.websiteoutlook.com", '//*[@id="analyse"]/div/input', webdriver)
    #     webout.collect_that_all()

    def test_maternal( self ):
        idecko = maternal_that_all( maternalURL, webdriver)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main( verbose = 2 )