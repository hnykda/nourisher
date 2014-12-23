'''
Created on Dec 22, 2014

@author: dan
'''

"""
Here are all customizables
"""

### DATABASE ###
DB_IP = "localhost"
DB_PORT = 5432
DB_NAME = "testdb"
DB_COLLECTION = "feeds"


### MATERNALSITE ###
DEFAULT_DRIVER = "phantomjs"

### VERBOSITY ###
VERBOSITY = 1


def get_setings():
    print( DB_COLLECTION, DB_PORT, DB_IP, DB_NAME, DEFAULT_DRIVER, VERBOSITY )
