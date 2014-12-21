from .feeder import feed_that_all
from nourisher.collector.maternalSite import maternal_that_all

def collect_all( origUrl ):
    '''Collects maximum informations about feed,
        saves them inside database and return info
    '''

    feedInfo = feed_that_all( origUrl )

    maternalInfo = maternal_that_all()

    return( feedInfo )
