'''
Created on Dec 20, 2014

@author: dan

Here are some utilities that might be useful
'''

from locale import setlocale, LC_ALL
from locale import atof
setlocale( LC_ALL, "en_US.UTF8" )

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
    
    Returns
    -------
    ObjectID: ObjectID of inserted document    
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

    ''' Get info from db by it's _id or objectid
    
    Parameters
    -----------
    idOfO: ID of object in database
    '''

    from pymongo import MongoClient
    from bson.objectid import ObjectId

    if type( idOfO ) == str:
        idOfO = ObjectId( idOfO )

    client = MongoClient( ip, port )
    db = client[dbName][collection]

    outData = db.find_one( {'_id' : idOfO} )

    client.disconnect()

    return( outData )

def get_id_of_last_inserted( dbName = "testdb", collection = "feeds",
                ip = "localhost", port = 5432 ):
    '''Get ObjectID of last inserted document
    from pymongo import MongoClient
    
    Returns
    -------
    ObjectID: last inserted document to collection
    '''
    from pymongo import MongoClient
    client = MongoClient( ip, port )
    db = client[dbName][collection]

    return ( db.find().sort( '_id' )[db.count() - 1]['_id'] )


def wrangle_numbers( vst ):
    ''' Converts string to numbers, if possible
    
    Handle even percents and also 
    
    Parameters
    ----------
    vst: string in form D%, D, D in en_US local, empty
    
    Returns
    -------
    float
    
    Note
    -----
    It will probably give some errors, but they can be handled 
    by IFs (better for debugging)
    '''

    if len( vst ) > 0:
        numb = vst[0]

        # percents to [0,1]
        if numb[-1] == "%":
            vysl = atof( numb[:-1] ) / 100

        # some webs return slash when no information are provided
        elif numb == "-":
            vysl = None

        # the rest should work normally - this will give errors
        else:
            vysl = atof( numb )
            # this was before -
            # try:
            #    vysl = atof(numb)
            # except:
            #    vysl = None

    elif vst == "":
        vysl = None


    return( vysl )

def time_to_dec( time ):
    try:
        t = time

        # no information provided
        if t == "-":
            return( None )

        pl = t.split( ":" )
        minutes = atof( pl[0] )
        secs = ( atof( pl[1] ) / 60 )
        ttime = minutes + secs
        return( ttime )

    except:
        print( "Nelze: ", time )
        return( None )
