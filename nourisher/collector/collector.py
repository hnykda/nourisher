from .feeder import feed_that_all

def collect_all( origUrl ):
    '''Collects maximum informations about feed,
        saves them inside database and return info
    '''

    feed = feed_that_all( origUrl )

    return( feed )
