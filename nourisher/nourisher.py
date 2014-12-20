from urllib.error import URLError
class Nourisher:
    '''Top-holder for everything next
    
    Atributes
    ----------
    origFeedUrl: Input URL of web feed
    '''

    origFeedUrl = None
    data = None

    def __init__( self, _origUrlofFeed ):
        self.origFeedUrl = _origUrlofFeed

        if self.check_response( _origUrlofFeed ) == True:
            pass
        else:
            raise URLError


    def check_response( self, origUrl ):
        '''Checks if page responds
        
        Atributes
        ---------
        Original URL of feed
        
        Returns
        -------
        Bool
        '''

        from urllib.request import urlopen

        try:
            urlopen( origUrl ).status
            return( True )
        except URLError:
            return( False )



    def collect_all( self ):
        '''Collects maximum of informations
        
        Notes
        ------
        
        Time stamp should be included!

        Returns
        -------
        Info
        '''

        if self.check_response( self.origFeedUrl ) == True:
            pass
        else:
            print( "Page is not responding! Returning None! - sorry for that" )
            return( None )

        from .collector import collector

        harve = collector.collect_all( self.origFeedUrl )

        self.data = harve

        return()
