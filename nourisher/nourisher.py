from urllib.error import URLError, HTTPError
from nourisher.utiliser import get_from_db, push_to_db, informer
class Nourisher:
    '''Top-holder for everything next
    
    Atributes
    ----------
    origFeedUrl: Input URL of web feed
    '''

    origFeedUrl = None
    dataID = None
    dataLoaded = None
    dataCleaned = None

    def __init__( self, _origUrlofFeed, ):
        self.origFeedUrl = _origUrlofFeed

        if self.check_response( _origUrlofFeed ) == True:
            pass
        else:
            # if no response is given, just push this to databse and
            # it means that there is nothing to collect
            push_to_db( {"origURL" : self.origFeedUrl} )
            raise URLError( "Can't connect to feed" )

    def get_objectid( self ):

        if self.dataID == None:
            print( "Trying to find out if is already in database" )
            from .utiliser import find_object_by_origurl
            obj = find_object_by_origurl( self.origFeedUrl )
            if obj == None:
                raise RuntimeError ( "Data hasn't been collected yet. Run collect_all()" )
            else:
                res = obj
                # Mongodb have UTC time, not local
                print( "Data have been already collected in  ", res.generation_time.isoformat() )
                return( res )
        else:
            return( self.dataID )

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
            sta = urlopen( origUrl ).status
            informer( "Page {0} is responding: ".format( origUrl ) + str( sta ) )
            return( True )
        except ( ConnectionResetError, URLError, HTTPError ):
            pass



    def collect_all( self ):
        '''Collects maximum of informations
        
        Notes
        ------
        
        Time stamp should be included!

        Returns
        -------
        ObjectID: ObjectID to database (and corresponding collection)
        '''

        if self.check_response( self.origFeedUrl ) == True:
            pass
        else:
            print( "Page is not responding! Returning None!" )
            return( None )

        from .collector import collector

        self.dataID = collector.collect_all( self.origFeedUrl )

    def retrieve_data( self ):
        """Retrieve data from database based on self.dataID"""

        objID = self.get_objectid()
        data = get_from_db( objID )
        self.dataLoaded = data
        informer( "Data retrieved for {0}".format( objID ) )
        return( data )

    def clean_data( self ):

        if self.dataLoaded == None:
            print( "Retrieve data first!" )
            raise

        from .cleaning import clean_that_all
        cleaned = clean_that_all( self.dataLoaded )
        self.dataCleaned = cleaned
        informer( "Data have been cleaned." )
        return( cleaned )

    def add_to_object_db( self, key, data ):
        '''Updates current dataID object with wished key'''
        from .utiliser import update_db_object

        res = update_db_object( {"_id" : self.dataID}, key, data )
        print( res )


