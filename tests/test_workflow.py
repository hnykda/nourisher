import unittest
import pandas as pd
from time import strftime
print( "\n" )
print( strftime( "%Y-%m-%d %H:%M:%S" ) )

import os
os.chdir( "../" )
print( os.path.abspath( "." ) )

testingUrl = 'http://www.huffingtonpost.com/news/authors/feed/'
# testingUrl = 'http://www.irinnews.org/top10.xml'


from nourisher.nourisher import Nourisher
from nourisher.utiliser import push_to_db, get_from_db

nour = Nourisher( testingUrl )

class TestWorkflow( unittest.TestCase ):

    def test_Flow( self ):
        nour.collect_all()

        self.assertEqual( type( pd.Series() ), type( nour.data ) )
        self.assertEqual( nour.data.shape, ( 17, ) )

    def test_db_save_and_load( self ):
        dictator = nour.data.to_dict()
        insId = push_to_db( dictator )
        retr = get_from_db( insId )

        check_list = ['author', 'bozo', 'href', 'info', 'language', 'version',
                      'link', 'n_of_entries', 'pub_freq', 'status', 'title',
                     ]
        for chck in check_list:
            self.assertEqual( retr[chck], nour.data[chck] )

# TestWorkflow().test_Flow()
# TestWorkflow().test_db_save_and_load()
