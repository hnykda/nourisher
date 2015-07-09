'''
Created on Dec 21, 2014

@author: dan
'''

from nourisher.utiliser import get_webdriver, scraper_prep
import unittest
from time import sleep

goodurls = ['www.huffingtonpost.com', "www.ihned.cz"]
badurls = ['www.asdsgsdfgdfgdfgdfgxxsa.com', 'asfasdfasdf.cz', "www.danielhnyk.cz"]

webdriver = get_webdriver()


class Test(unittest.TestCase):
    def scraper_collect(self, scraper, url):
        scraper.get_maternal(url)
        scraper.collect_that_all()

        return scraper.scrapedData

    def test_Alexa(self):
        scrp = scraper_prep("alexa", webdriver)
        with self.assertRaises(RuntimeError) as cm:
            res1 = self.scraper_collect(scrp, badurls[0])
        sleep(30)

        res2 = self.scraper_collect(scrp, goodurls[0])

    def test_Ranks(self):
        scrp = scraper_prep("ranks", webdriver)
        with self.assertRaises(RuntimeError) as cm:
            res1 = self.scraper_collect(scrp, badurls[0])
        sleep(30)

        res2 = self.scraper_collect(scrp, goodurls[0])

    def test_Webout(self):
        scrp = scraper_prep("websiteout", webdriver)
        with self.assertRaises(RuntimeError) as cm:
            res1 = self.scraper_collect(scrp, badurls[0])

        sleep(30)

        res2 = self.scraper_collect(scrp, goodurls[0])

    def test_Urlm(self):
        scrp = scraper_prep("urlm", webdriver)
        with self.assertRaises(RuntimeError) as cm:
            res1 = self.scraper_collect(scrp, badurls[0])
        sleep(30)

        res2 = self.scraper_collect(scrp, goodurls[0])

#    def __del__(self):
#        webdriver.quit()


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main(verbose=2)
