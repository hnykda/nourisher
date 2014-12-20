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
        from pymongo import MongoClient

        client = MongoClient( "localhost", 5432 )
        db = client.testdb
        feeds = db.feeds

        dictator = nour.data.to_dict()

        insid = feeds.insert( dictator )

        retr = feeds.find( {"_id":insid } )[0]
        client.disconnect()

        self.assertEqual( retr["href"], nour.data["href"] )
        # self.assertEqual( retr["entries"], nour.data["entries"] )

# TestWorkflow().test_Flow()
# TestWorkflow().test_db_save_and_load()
