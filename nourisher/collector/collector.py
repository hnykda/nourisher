from .feeder import feed_that_all
from nourisher.collector.maternalSite import maternal_that_all
from ..utiliser import maternal_url_extractor

def collect_all( origUrl ):
    '''Collects maximum informations about feed,
        saves them inside database and return info
    '''

    total = {}

    feedInfo = feed_that_all( origUrl )
    finUrls = feedInfo["entries"]["finalUrl"]
    maternalUrlByAlexa = maternal_url_extractor( finUrls )
    maternalInfo = maternal_that_all( maternalUrlByAlexa )

    total.update( feedInfo.to_dict() )
    total.update( maternalInfo )

    return( total )
