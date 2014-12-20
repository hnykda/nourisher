'''
Created on Dec 20, 2014

@author: dan

Here are some utilities that might be useful
'''

def mean_a_var_z_listu( lentry ):
    """Returns mean and std from list of numbers
    
    Parameters
    -----------
    Array of numbers
    
    Returns
    -------
    (mean, std)
    """
    import numpy as np

    return ( np.mean( lentry ), np.std( lentry ) )

def push_to_db( inpObj, dbName = "testdb", collection = "feeds",
                ip = "localhost", port = 5432 ):

    ''' Saves inpObj to MongoDB and returns it's _id
    
    Parameters
    -----------
    inpObj: Series (is converted to dict), dict, or something pymongo can serialize to JSON
    '''

    import pandas as pd
    if type( inpObj ) == type( pd.Series ):
        inpObj = inpObj.to_dict()

    from pymongo import MongoClient

    client = MongoClient( ip, port )
    db = client[dbName][collection]

    insID = db.insert( inpObj )

    client.disconnect()

    return( insID )

def get_from_db( idOfO, dbName = "testdb", collection = "feeds",
                ip = "localhost", port = 5432 ):

    ''' Get info from db by it's _id
    
    Parameters
    -----------
    idOfO: ID of object in database
    '''

    from pymongo import MongoClient

    client = MongoClient( ip, port )
    db = client[dbName][collection]

    outData = db.find( idOfO )

    client.disconnect()

    return( outData )

