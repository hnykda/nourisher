'''
Created on Dec 21, 2014

@author: dan
'''

from nourisher.collects.collector import Collector

import unittest
testurl1 = 'http://www.huffingtonpost.com/news/authors/feed/'
testurl2 = 'http://www.irinnews.org/top10.xml'
testurl3 = 'http://css-tricks.com/frosting-glass-css-filters/feed/'

class Test( unittest.TestCase ):
    def test_collector(self):
        col = Collector()

        ids = []
        for url in [testurl1, testurl2, testurl3]:
            print("Pokracujeme")
            ids.append(col.collect_for_orig(url))
            from time import sleep
            print("Spim 60 sec")
            sleep(60)

        print(ids)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main( verbose = 2 )