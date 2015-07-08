"""
Created on Dec 24, 2014

@author: dan
"""
from nourisher import settings as setl
from nourisher import utiliser

"""
This module is for managing whole collection

Basically it's a little ORM
"""


class Collection:
    """Collection for whole dataset
    
    Parameters
    ----------
    datasetID : list of ObjectID
        ObjectIDs of all objects in database    
    """

    datasetID = None
    fetched = False
    cur = None

    def __init__(self):
        from pymongo import MongoClient

        client = MongoClient(setl.DB_IP, setl.DB_PORT)
        coll = client[setl.DB_NAME][setl.DB_COLLECTION]

        self.cur = coll

    def get_ids(self):
        """Load ObjectIDs of items in collection
        
        Returns
        -------
        list of ObjectID
            ObjectIDs of all items in database, saves them to self.datasetID
        """
        if self.cur is None:
            raise RuntimeError("Fetch IDs first")

        ids = [item["_id"] for item in self.cur.find({})]
        self.datasetID = ids
        self.fetched = True
        return ids

    def get_collumn(self, key):
        """Get first level column of every fetched object
        
        If key is not found, only None for given URL is returned
        
        Parameters
        ----------
        key : string
            one of key in database
        
        Returns
        -------
        dict
            in form {ObjectID1 : val1, ...}
        """

        if not self.fetched:
            raise KeyError("Fetch IDs first")

        total = {}
        counterEmptiness = True
        for oid in self.datasetID:
            try:
                total.update({oid: self.cur.find_one({"_id": oid})[key]})
                counterEmptiness = False
            except KeyError:
                total.update({oid: None})

        if counterEmptiness:
            raise KeyError("No such key in any of objects")

        setattr(self, key, total)
        utiliser.informer(
            "Data saved under {0} attribut. Number of None values: {1}".format(key, self.count_nones(key)))

        return getattr(self, key)

    def count_nones(self, key):
        """Count None values in column"""

        try:
            getattr(self, key)
        except KeyError:
            raise KeyError("Data are not fetched to this attribut")

        cnones = lambda x: True if x is None else False
        count = len(list(filter(cnones, [val[1] for val in getattr(self, key).items()])))

        return count

    @staticmethod
    def init_nourisher_by_id(ide):
        """
        Takes ObjectID, tries to find out this ID in database, create 
        new Nourisher object initialized with dataID, dataretrieved and
        make a new cleaning on them.
        
        Parameters
        ----------
        ide
            ObjectID of wished object
        
        Returns
        -------
        Nourisher instance
        """

        from nourisher import nourisher

        raw_data = utiliser.get_from_db(ide)
        url = raw_data["origURL"]
        nour = nourisher.Nourisher(url)
        nour.dataID = nour.get_objectid()
        nour.retrieve_data()
        nour.clean_data()
        return nour


# def analyze_collection( self ):
#         """
#         Analyze number of missing values, return wrong items...
#
#         Note
#         -----
#         Memory consuming!
#         """
#
#         if self.fetched == False:
#             raise KeyError ( "Get IDs first!" )
#
#         evr = self.cur.find( {} )
#
#         # no data at all
#         fetchEvr = [i for i in evr]
#
#         # missing data per domain
#
#         setattr( self, "collection_info", dataAnalysis )

#     def collect_cols( self, lkeys ):
#         """Collects keys in lkeys and make a collection from that
#
#         Parameters
#         ----------
#         lkeys : list of strings
#             contains name of keys from which to build a collections
#
#         Returns
#         -------
#         dict
#             in format `{key1 : [data1], key2 : [data2], ...}`
#         """
#
#         valsList = []
#         for key in lkeys:
#             valsList.append( {key : self.get_collumn( key )} )
#
#         dataTotal = {}
#         for lst in valsList:
#             idIn = {}
#             for curID, val in lst.items():
#                 idIn.update( {curID : val} )
#             dataTotal.update( idIn )


class MultiScrapper:
    """This is for collecting data for multiple source URLs
    
    Attributes
    ----------
    sourceURLs : list of strings
        list of URLs which we want to scrap
    goodOnes : list of strings
        urls which were processed correctly
    badOnes  : list of strings
        urls which were processed correctly
    counter : int
        number of processed URLs so far
    """

    sourceURLs = []
    goodOnes = []
    badOnes = []
    counter = 0

    def scrap_data(self, startingPoint=0, sleepInt=300, logFile="scrap.log"):
        """Scrap all URLs from sourceURLs
        
        Parameters
        ----------
        startingPoint : int
            from which url in sourceURLs should be started
        sleepInt : int
            number of seconds to wait between every loop (because of bans on some servers)
        logFile : strings
            path to file where you want to save log
        """

        import time
        import sys
        import traceback
        from nourisher.nourisher import Nourisher

        self.counter = startingPoint + 1
        for url in self.sourceURLs:
            now = time.time()
            try:
                utiliser.informer("\nProcessing {0}/{1}: {2}".format(
                    self.counter, len(self.sourceURLs), url))
                nour = Nourisher(url)
                nour.collect_all()
                nour.retrieve_data()
                nour.clean_data()
                nour.update_object_db("cleaned", nour.dataCleaned)
                self.goodOnes.append(url)
            except KeyboardInterrupt as ex:
                # if ctrl+c is pressed exit
                utiliser.informer("So far were processed {0} ({1}) URLs. ".format(self.counter, url))
                raise ex
            except:
                # but if anything else - continue
                sysEr = sys.exc_info()
                tracb = traceback.format_exc()
                utiliser.informer(sysEr, tracb)
                self.badOnes.append((url, tracb))

                with open(logFile, "a", encoding="utf-8") as logf:
                    logf.writeline(url)
                    logf.writeline("\n".join(tracb))

            utiliser.informer("It tooks: {0} seconds. \n---------------\n".format(time.time() - now))
            time.sleep(sleepInt)
            self.counter += 1

    def fetch_urls(self, filePath):
        """Get urls from file and appends them to sourceURLs.
        
        This file must have one url address on every line, encoding utf-8.
        """

        with open(filePath, "r", encoding="utf-8") as ifile:
            lurls = ifile.readlines()
            urls = [line.split("\n")[0] for line in lurls]

        self.sourceURLs += urls
        utiliser.informer(self.sourceURLs, level=2)
