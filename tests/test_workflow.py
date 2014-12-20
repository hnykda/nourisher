import unittest
import pandas as pd


import os
os.chdir( "../" )
print( os.path.abspath( "." ) )

testingUrl = 'http://www.huffingtonpost.com/news/authors/feed/'
# testingUrl = 'http://www.irinnews.org/top10.xml'


from nourisher.nourisher import Nourisher

nour = Nourisher( testingUrl )

class TestWorkflow( unittest.TestCase ):

    def test_Flow( self ):
        nour.collect_all()

        self.assertEqual( type( pd.Series() ), type( nour.data ) )
        self.assertEqual( nour.data.shape, ( 17, ) )

    def test_db_save_and_load( self ):

        """Tohle predelat pomoci push/get db"""
        from pymongo import MongoClient

        client = MongoClient( "localhost", 5432 )
        db = client.testdb
        feeds = db.feeds

        dictator = nour.data.to_dict()

        insid = feeds.insert( dictator )

        retr = feeds.find( {"_id":insid } )[0]
        client.disconnect()

        check_list = ['author', 'bozo', 'href', 'info', 'language', 'version',
                      'link', 'n_of_entries', 'pub_freq', 'status', 'title',
                     ]
        for chck in check_list:
            self.assertEqual( retr[chck], nour.data[chck] )

# TestWorkflow().test_Flow()
# TestWorkflow().test_db_save_and_load()
