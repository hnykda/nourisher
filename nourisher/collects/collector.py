import logging
log = logging.getLogger(__name__)

from .feeder import feed_that_all
import time
from utiliser import scraper_prep, get_webdriver

class Collector():
    """ Wrapper for collecting
    """

    def __init__(self, wdriver_name, maternal_scrapers = ["urlm", "websiteout", "ranks", "alexa"]):
        
        self.wdriver_name = wdriver_name

        self.driver = get_webdriver(wdriver_name)
        self.load_scrappers(maternal_scrapers)


    def load_scrappers(self, scrapers_names):
        for name in scrapers_names:
            setattr(self, name, scraper_prep(name, self.wdriver_name))

    def collect_maternal(self, finUrls, origUrl):
        total = {}

        # alexa must be first, because she returns the
        # true address
        log.debug("Nechavama alexu uhadnout adresu.")
        if finUrls != []:
            article_url = finUrls[0] # url of first article
        else:
            article_url = origUrl # if no articles present, try the original one
        self.alexa.get_maternal(article_url)
        maternal_url = self.alexa.guessed_maternal_url

        try:
            log.debug("Alexa sbira data.")
            self.alexa.collect_that_all()
            total.update({"alexa": self.alexa.scrapedData})
        except RuntimeError:
            log.debug("Alexa nic nema.")
            total.update({"alexa" : None})

        rest = {"urlm" : self.urlm,
                "websiteout": self.websiteout,
                "ranks" : self.ranks}
        for sname, scrpr in rest.items():
            log.debug(sname + " sbira data.")
            try:
                scrpr.get_maternal(maternal_url)
                scrpr.collect_that_all()
                total.update({sname: scrpr.scrapedData})
                log.debug("Succeded.")
                #sleep(ST)
            except RuntimeError:
                log.debug("Scrapper neuspel")
                total.update({sname: None})

        return total, maternal_url

    def collect_for_orig(self, orig_url):

        startTime = time.time()

        total = {}
        feedInfo, finUrls = feed_that_all(orig_url)

        maternalInfo, maternal_url = self.collect_maternal(finUrls, orig_url)

        total.update({"feedInfo": feedInfo})
        total.update(maternalInfo)
        total.update({"origURL": orig_url})
        total.update({"maternalURL": maternal_url})
        total.update({"datetime_of_collection" : time.strftime("%Y-%m-%d %H:%M:%S")})

        log.info("Collecting data took: {0}".format(time.time() - startTime) + " seconds")
        return total

    def restart_driver(self):
        self.driver.quit()
        self.driver = get_webdriver(self.wdriver_name)
