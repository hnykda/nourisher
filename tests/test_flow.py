import unittest
from time import strftime
from nourisher.collector import collector
print( "\n" )
print( strftime( "%Y-%m-%d %H:%M:%S" ) )

import os
os.chdir( "../" )
print( os.path.abspath( "." ) )

# testingUrl = 'http://www.allonlinecoupons.com/rss/teachers-school-supply.xml'
testingUrl = 'http://smittyspeaks.weebly.com/1/feed'
# testingUrl = 'www.pornoquantum.tumblr.com'


from nourisher.nourisher import Nourisher
from nourisher.utiliser import push_to_db, get_from_db

nour = Nourisher( testingUrl )

class Testfeeder( unittest.TestCase ):
    def test_A_Collect( self ):
        """Tries to collect everything"""

        nour.collect_all()
        nour.retrieve_data()
        nour.clean_data()
        retr = get_from_db( nour.dataID )

        self.assertEqual( nour.dataLoaded["origURL"], retr["origURL"] )


        # self.assertNotEqual( nour.data, None, "Nothing has been saved" )

        # pushID = push_to_db( nour.data )
        # retr = get_from_db( pushID )

#         FIcheck_list = ['author', 'bozo', 'href', 'info', 'language', 'version',
#                       'link', 'n_of_entries', 'pub_freq', 'status', 'title',
#                      ]
#
#         for chck in FIcheck_list:
#             self.assertEqual( retr["feedInfo"][chck], nour.data["feedInfo"][chck] )

#     def test_ZFeedInfo( self ):
#         """Checks if the collected feed info match the one from retrieved object
#         TODO: In the future make better asserts - only somes are currently checked
#         """
#         FIcheck_list = ['author', 'bozo', 'href', 'info', 'language', 'version',
#                       'link', 'n_of_entries', 'pub_freq', 'status', 'title',
#                      ]
#         for chck in FIcheck_list:
#             self.assertEqual( retr["feedInfo"][chck], nour.data["feedInfo"][chck] )
#
#     def test_ZAlexa( self ):
#         """Checks if the collected Alexa info match the one from retrieved object
#         TODO: In the future make better asserts - only somes are currently checked
#         """
#         AcheckList = ["link", "rankInCountry", "bounceRate"]
#         for chck in AcheckList:
#             self.assertEqual( self.retr["alexa"][chck], nour.data["alexa"][chck] )
#
#     def test_ZWebsitout( self ):
#         """Checks if the collected websioutlook info match the one from retrieved object
#         TODO: In the future make better asserts - only somes are currently checked
#         """
#         checkList = ["link", "estimatedWorth", "pageRank"]
#         for chck in checkList:
#             self.assertEqual( self.retr["websiteout"][chck], nour.data["websiteout"][chck] )
#
#     def test_ZUrlm( self ):
#         """Checks if the collected urlm info match the one from retrieved object
#         TODO: In the future make better asserts - only somes are currently checked
#         """
#         checkList = ["externalLinks", "rankInCountry", "estimatedWorth"]
#         for chck in checkList:
#             self.assertEqual( self.retr["urlm"][chck], nour.data["urlm"][chck] )
#
#     def test_ZRanks( self ):
#         """Checks if ranks are OK"""
#         self.assertEqual( self.retr["ranks"], nour.data["ranks"] )

# TestWorkflow().test_Flow()
# TestWorkflow().test_db_save_and_load()
