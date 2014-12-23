from .feeder import feed_that_all
from .maternalSite import maternal_that_all

from ..utiliser import maternal_url_extractor, push_to_db
from nourisher.utiliser import informer


def collect_all( origUrl ):
    '''Collects maximum informations about feed,
        saves them inside database and return info
    '''

    total = {}

    _feedInfo = feed_that_all( origUrl )
    feedInfo = _feedInfo[0]
    informer( "feedInfo collected." )

    # this is hack - no list needed
    finUrls = _feedInfo[1]
    maternalUrlByAlexa = maternal_url_extractor( finUrls )

    maternalInfo = maternal_that_all( maternalUrlByAlexa )

    total.update( {"feedInfo" : feedInfo} )
    total.update( maternalInfo )
    total.update( {"origURL" : origUrl} )

    resID = push_to_db( total )

    return( resID )
