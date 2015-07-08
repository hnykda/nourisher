from .feeder import feed_that_all
from .maternalSite import maternal_that_all

from ..utiliser import maternal_url_extractor, push_to_db
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

    # this is hack - no list needed
    finUrls = _feedInfo[1]
    maternalUrlByAlexa = maternal_url_extractor(finUrls)

    maternalInfo = maternal_that_all(maternalUrlByAlexa)

    total.update({"feedInfo": feedInfo})
    total.update(maternalInfo)
    total.update({"origURL": origUrl})
    total.update({"maternalURL": maternalUrlByAlexa})

    resID = push_to_db(total)
    informer("Collection data took: {0}".format(time.time() - startTime) + " seconds", level=2)

    return resID


def collect_maternal(maternalURL, _deal=None):
    """Collect data for maternal URL
    
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
