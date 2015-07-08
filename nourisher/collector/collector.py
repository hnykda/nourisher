from .feeder import feed_that_all
from .maternalSite import maternal_that_all

from ..utiliser import maternal_url_extractor, push_to_db, get_webdriver
from nourisher.utiliser import informer


def collect_all(origUrl):
    """Collects maximum informations about the feed,
    saves them inside database and returns ObjectID

    Parameters
    ----------
    origUrl: string
        original URL of the input feed

    Return
    ------
    ObjectID: ObjectID
        of data saved in database
    """

    import time

    startTime = time.time()
    total = {}

    _feedInfo = feed_that_all(origUrl)
    feedInfo = _feedInfo[0]
    informer("feedInfo collected.")

    webdriver = get_webdriver()  # initialize webdriver only once and not every scrapper
    finUrls = _feedInfo[1]  # this is hack - no list needed
    maternalUrlByAlexa = maternal_url_extractor(finUrls, webdriver)

    maternalInfo = maternal_that_all(maternalUrlByAlexa, webdriver)

    total.update({"feedInfo": feedInfo})
    total.update(maternalInfo)
    total.update({"origURL": origUrl})
    total.update({"maternalURL": maternalUrlByAlexa})

    resID = push_to_db(total)
    informer("Collection data took: {0}".format(time.time() - startTime) + " seconds", level=2)

    return resID


def collect_maternal(maternalURL, _deal=None):
    """Collect data for maternal URL

    Only for testing
    
    Parameters
    ----------
    maternalURL : string
        maternal URL
    deal : list of strings
        names of scrapers from which to get data from
    
    Returns
    -------
    dict
        scrapped data
    """
    if not _deal:
        _deal = ["websiteout", "urlm", "ranks", "alexa"]

    data = maternal_that_all(maternalURL, _deal)
    return data
