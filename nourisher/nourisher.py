import logging
log = logging.getLogger(__name__)

from nourisher.utiliser import get_from_db, push_to_db, informer

class Nourisher:
    """Top-holder for everything next

    Atributes
    ----------
    origFeedUrl: string
        Input URL of web feed
    dataID : ObjectID
        ObjectID of data in database
    data : dict
        retrieved data from database
    dataCleaned : dict
        data cleaned
    """

    origFeedUrl = None
    dataID = None
    data = None
    dataCleaned = None

    def __init__(self, _origUrlofFeed):
        """Init

        Checks if feed responds.

        Parameters
        ----------
        _origUrlOfFeed: string
            feed of url which should be examined"""

        self.origFeedUrl = _origUrlofFeed

        if self.check_response(_origUrlofFeed):
            pass
        else:
            # if no response is given, just push this to databse and
            # it means that there is nothing to collect
            push_to_db({"origURL": self.origFeedUrl})
            raise ConnectionError("Can't connect to feed")

    def get_objectid(self):
        """Try to find out by origFeedUrl if it is already in database
        and if it is, it is returned
        
        When more than one are found, last one is returned
        
        Returns
        -------
        ObjectID
            ObjectID of existing item in database which has been inserted as a lastone
            
        Raise
        ------
        RuntimeError
            If no data have been collected yet, RuntimError is raised
        """

        if self.dataID is None:
            print("Trying to find out if this URL is already in database")
            from .utiliser import find_objects_by_origurl

            obj = find_objects_by_origurl(self.origFeedUrl)
            if obj is None:
                raise RuntimeError("Data hasn't been collected yet. Run collect_all()")
            else:
                res = obj
                # Mongodb have UTC time, not local
                # print( "Data have been already collected in  ", res.generation_time.isoformat() )
                return res
        else:
            return self.dataID

    @staticmethod
    def check_response(origUrl):
        """Checks if page responds

        TODO: should return True or False, not True or exception

        Atributes
        ---------
        origUrl : string
            Original URL of feed

        Returns
        -------
        Bool
            True if page responds, else exception
        """

        import requests

        try:
            gmet = requests.get(origUrl, timeout=10)
            statusCode = gmet.status_code

            if statusCode == 404:
                raise ConnectionError("Page is not responding 404")
            else:
                informer("Page {0} is responding: ".format(origUrl) + str(statusCode))
                return True

        except (ConnectionError, requests.exceptions.Timeout) as ex:
            raise ex

    def collect_all(self, collector):
        """Collects maximum of informations
        """

        if self.check_response(self.origFeedUrl):
            pass
        else:
            print("Page is not responding! Returning None!")
            return None

        total = collector.collect_for_orig(self.origFeedUrl)

        resID = push_to_db(total)
        self.dataID = resID
        self.data = total

    @staticmethod
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

        from nourisher.collects.collector import collect_maternal

        data = collect_maternal(maternalURL, _deal)

        return data

    def retrieve_data(self):
        """Retrieve data from database based on self.dataID
        
        Returns
        -------
        dict
            object from database with current self.dataID
        """

        objID = self.get_objectid()
        data = get_from_db(objID)
        self.data = data
        informer("Data retrieved for {0}".format(objID))
        return data

    def clean_data(self):
        """Runs cleaning on collected (or retrieved) data
        
        Returns
        -------
        dict
            with cleaned and wrangled data
        """

        if self.data is None:
            raise RuntimeError("Retrieve data first!")

        from .cleaning import clean_that_all

        cleaned = clean_that_all(self.data)
        self.dataCleaned = cleaned
        informer("Data have been cleaned.")
        return cleaned

    def update_object_db(self, key, data):
        """Updates current dataID object with wished values under key

        Parameters
        ----------
        key : string
            name of attribute under which to save the data
        data : dict, something JSON seriazable
            data to save

        Returns
        -------
        ObjectID
            ID under which were data saved (current dataID)
        """

        from .utiliser import update_db_object

        res = update_db_object({"_id": self.dataID}, key, data)
        print(res)
