import logging
log = logging.getLogger(__name__)

"""
Created on Dec 22, 2014

@author: dan
"""

"""
Here is possible to set customizables - global variables
"""

### DATABASE ###
DB_IP = "localhost"  # IP where is MongoDB running
DB_PORT = 5432  # port where is database running
DB_NAME = "testdb"  # Name of default database
DB_COLLECTION = "feeds"  # Name of collection in database


### MATERNALSITE ###
# which selenium.webdriver and settings
# should be used for scrapping. Possible values in maternaSite.Scraper
DEFAULT_DRIVER = "phantomjs"

### VERBOSITY ###
VERBOSITY = 1  # Verbosity of std output (currently implemented 0, 1, 2)

def get_setings():
    """Print current settings"""
    log.debug(DB_COLLECTION + " " + str(DB_PORT) + " " + DB_IP + " " +  DB_NAME + " " + DEFAULT_DRIVER + " " + str(VERBOSITY ))

# class SETTER:
#     ### DATABASE ###
#     DB_IP = "localhost"  # IP where is MongoDB running
#     DB_PORT = 5432  # port where is database running
#     DB_NAME = "testdb"  # Name of default database
#     DB_COLLECTION = "feeds"  # Name of collection in database
#
#
#     ### MATERNALSITE ###
#     # which selenium.webdriver and settings
#     # should be used for scrapping. Possible values in maternaSite.Scraper
#     DEFAULT_DRIVER = "phantomjs"
#
#     ### VERBOSITY ###
#     VERBOSITY = 1  # Verbosity of std output (currently implemented 0, 1, 2)
#
#     def set_db_collection( self, name ):
#         self.DB_COLLECTION = name
#
#     def get_db_collection( self ):
#         return( self.DB_COLLECTION )
