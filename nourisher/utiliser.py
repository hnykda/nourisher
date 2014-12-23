'''
Created on Dec 20, 2014

@author: dan

Here are some utilities that might be useful
'''

from nourisher import settings as lset
from pymongo import MongoClient

def informer( msg, *args, level = 1, rewrite = False ):

    # we don't want any errors from logging...
    try:
        if lset.VERBOSITY < level:
            pass
        elif lset.VERBOSITY >= level:
            if rewrite == False:
                print( msg )
                if args:
                    for arg in args:
                        print( arg )
            elif rewrite == True:
                print( "\r" + msg, end = "" )
                if args:
                    for arg in args:
                        print( "\r" + arg, end = "" )

    except:
        import sys
        print( "Can't print message because of ", sys.exc_info() )

def push_to_db( inpObj, dbName = lset.DB_NAME, collection = lset.DB_COLLECTION,
                ip = lset.DB_IP, port = lset.DB_PORT ):

    ''' Saves inpObj to MongoDB and returns it's _id
    
    Parameters
    -----------
    inpObj: Series (is converted to dict), dict, or something pymongo can serialize to JSON
    
    Returns
    -------
    ObjectID: ObjectID of inserted document    
    '''

    client = MongoClient( ip, port )
    db = client[dbName][collection]

    insID = db.insert( inpObj )
    informer( "Saving to database under ObjectID: ", str( insID ) )

    client.disconnect()

    return( insID )

def get_from_db( idOfO, dbName = lset.DB_NAME, collection = lset.DB_COLLECTION,
                ip = lset.DB_IP, port = lset.DB_PORT ):

    ''' Get info from db by it's _id or objectid
    
    Parameters
    -----------
    idOfO: ID of object in database
    '''

    from bson.objectid import ObjectId

    if type( idOfO ) == str:
        idOfO = ObjectId( idOfO )

    client = MongoClient( ip, port )
    db = client[dbName][collection]

    outData = db.find_one( {'_id' : idOfO}, {"_id" : 0} )

    client.disconnect()

    return( outData )

def get_id_of_last_inserted( dbName = lset.DB_NAME, collection = lset.DB_COLLECTION,
                ip = lset.DB_IP, port = lset.DB_PORT ):
    '''Get ObjectID of last inserted document
    from pymongo import MongoClient
    
    Returns
    -------
    ObjectID: last inserted document to collection
    '''
    client = MongoClient( ip, port )
    db = client[dbName][collection]

    return ( db.find().sort( '_id', -1 )[0]["_id"] )

def update_db_object( finder, key, value, dbName = lset.DB_NAME, collection = lset.DB_COLLECTION,
                ip = lset.DB_IP, port = lset.DB_PORT ):
    '''Update object in db
    
    Parameters
    -----------
    finder: dict by which we should find {key : value}
    key: under this name value will be added
    value: data to add under key
    '''
    client = MongoClient( ip, port )
    db = client[dbName][collection]

    res = db.update( finder, {"$set" : {key: value}} )
    return( res )

def find_object_by_origurl( origUrl, dbName = lset.DB_NAME, collection = lset.DB_COLLECTION,
                ip = lset.DB_IP, port = lset.DB_PORT ):
    '''Try to find object by original URL of feed'''

    client = MongoClient( ip, port )
    db = client[dbName][collection]

    try:
        allRes = db.find( {"origURL" : origUrl} ).sort( '_id', -1 )
        res = allRes[0]["_id"]
    except IndexError:
        res = None

    # TODO: Slow! But after find is fetched by res, allRes is empty...
    informer( "Object(s) by URL found: ", [( obj["_id"], obj["_id"].generation_time.isoformat() )
                                           for obj in db.find( {"origURL" : origUrl} ).sort( '_id', -1 )] )
    return( res )

def maternal_url_extractor( finalLinks ):
    ''' Try to find out most probable maternal URL 
    based on entries
    
    Parameters
    ----------
    True entries finalUrls
    
    Returns
    -------
    string: maternal URL (in www.maternalurl.*)
    
    Note
    -----
    Alexa is maybe better!
    
    '''

    # beru adresu prvniho clanku
    testUrl = finalLinks[0]

    from selenium import webdriver

    wdriver = webdriver.PhantomJS()
    # wdriver = webdriver.Firefox()
    wdriver.get( r'http://www.alexa.com/' )
    inputField = wdriver.find_element_by_xpath( '//*[@id="alx-content"]/div/div/span/form/input' )
    inputField.clear()
    inputField.send_keys( testUrl )
    inputField.submit()

    text = wdriver.find_element_by_xpath( '//*[@id="js-li-last"]/span[1]/a' ).text

    informer( "Alexa thinks that the maternal URL is: " + str( "www." + text ) )
    return( 'www.' + text )

    # OK, NECHAME TO NA ALEXE!
#     from tldextract import tldextract
#
#     # these are domains, which host another websites - for them
#     # there must be added subdomain
#     stopSites = ["blogpost.com", "wordpress.com"]
#
#     # these are stop words which are boring - like feeds, feed
#     stopWords = ["feed", "feeds"]
#
#     regDom = []
#     subDom = []
#     origDom = []
#
#     for link in finalLinks:
#         extr = tldextract.extract( link )
#         reg = extr.registered_domain
#         regDom.append( reg )
#
#         _sub = extr.subdomain.split( "." )
#         subDom.append( _sub )
#
#
#         if _sub[-1] == 'www':
#             origDom = 'www' + reg
#         # this is bad - maybe even lower higher domains should be joined
#         elif reg in stopSites:
#             origDom = _sub[-1] + reg
#         elif _sub[-1] in stopWords:
#             origDom = 'www' + reg
#         else:
