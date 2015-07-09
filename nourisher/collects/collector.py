import logging
log = logging.getLogger(__name__)

from .feeder import feed_that_all

from ..utiliser import scraper_prep, get_webdriver

class Collector():
    """ Wrapper for collecting
    """

    def __init__(self, maternal_scrapers = ["urlm", "websiteout", "ranks", "alexa"],
                 wdriver=get_webdriver()):
        self.driver = wdriver
        self.load_scrappers(maternal_scrapers)


    def load_scrappers(self, scrapers_names):
        for name in scrapers_names:
            setattr(self, name, scraper_prep(name, self.driver))

    def collect_maternal(self, finUrls):
        total = {}

        # alexa must be first, because she returns the
        # true address
        log.debug("Nechavama alexu uhadnout adresu.")
        article_url = finUrls[0] # url of first article
        self.alexa.get_maternal(article_url)
        maternal_url = self.alexa.guessed_maternal_url
        log.debug("Alexa sbira data.")
        self.alexa.collect_that_all()
        total.update({"alexa": self.alexa.scrapedData})

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

        import time
        startTime = time.time()

        total = {}
        feedInfo, finUrls = feed_that_all(orig_url)

        maternalInfo, maternal_url = self.collect_maternal(finUrls)

        total.update({"feedInfo": feedInfo})
        total.update(maternalInfo)
        total.update({"origURL": orig_url})
        total.update({"maternalURL": maternal_url})

        log.info("Collecting data took: {0}".format(time.time() - startTime) + " seconds")
        return total
