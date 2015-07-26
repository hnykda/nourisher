import logging
log = logging.getLogger(__name__)

"""
Created on Dec 20, 2014

@author: dan

Here are some utilities that might be useful
"""

import settings as lset
from pymongo import MongoClient

def get_db_driver(db_name=lset.DB_NAME, ip=lset.DB_IP, port=lset.DB_PORT):

    client = MongoClient(ip, port)
    db = client[db_name]

    return db

def fetch_doc_url_and_lock(db_driver, source_collection_name, lock_collection_name, error_collection_name,
                           random_order, ignore_error_check):

    log.debug("Trying to get some source URL... ")

    if not random_order:
        document = db_driver[source_collection_name].find_one()  # potrebuji vyextrahovat orig_URL a id_
    else:
        from random import randint
        random_record_ix = randint(0, db_driver[source_collection_name].count())
        document = db_driver[source_collection_name].find()[random_record_ix]

    if document is None:
        log.debug("No URL has been found. Setting to False")
        return False

    # check lock file
    lock_existence = db_driver[lock_collection_name].find_one(document["_id"])
    # check if error presents
    error_existence = True
    if not ignore_error_check:
        log.debug("Checkuji pro error.")
        error_existence = db_driver[error_collection_name].find_one({"orig_url" : document["orig_url"]})
        log.debug("Nalezen error record? Vysledek hledani: {}".format(error_existence))

    check = 0
    while (lock_existence is not None) or (error_existence is not None):
        from random import randint
        random_record_ix = randint(0, db_driver[source_collection_name].count())
        document = db_driver[source_collection_name].find()[random_record_ix]
        lock_existence = db_driver[lock_collection_name].find_one(document["_id"])
        error_existence = db_driver[error_collection_name].find_one({"orig_url" : document["orig_url"]})
        check += 1
        log.debug("Existuje lock a nebo zdroj jiz v minulosti vyhodil chybu.")

        if check >= 10:
            raise RuntimeError("It seems there is something wrong in this loop.")

    log.debug("Appropriate URL found: {}. Creating lock record.".format(document["orig_url"]))
    db_driver[lock_collection_name].insert(document)
    log.debug("Lock record created.")

    log.info("Number of unprocessed URLs: {}".format(db_driver[source_collection_name].count()))
    return document


def push_to_db(inpObj, dbName=lset.DB_NAME, collection=lset.DB_COLLECTION,
               ip=lset.DB_IP, port=lset.DB_PORT):
    """ Saves inpObj to MongoDB and returns it's _id

    Parameters
    -----------
    inpObj: dict, or something pymongo can serialize to JSON
        Object which should be pushed to database
    dbName: string, optional
        default in settings, name of database to write into
    collection: string, optional
        default in settings, Name of collection to write into
    ip: string, optional
        default in settings, IP where is MongoDB running
    port: interger, optional
        default in settings, port where is MongoDB running

    Returns
    -------
    ObjectID: ObjectID
        ObjectID of inserted document
    """

    client = MongoClient(ip, port)
    db = client[dbName][collection]

    insID = db.insert(inpObj)
    log.debug("Saving to {0} database, {1} collection under ObjectID: ".format(dbName, collection) + str(insID))

    client.close()

    return insID


def get_from_db(idOfO, dbName=lset.DB_NAME, collection=lset.DB_COLLECTION,
                ip=lset.DB_IP, port=lset.DB_PORT):
    """ Get info from db by it's _id or objectid

    Parameters
    -----------
    idOfO: ID in string, ObjectID
        of object which we want to retrieve data
    dbName: string, optional
        default in settings, name of database to write into
    collection: string, optional
        default in settings, Name of collection to write into
    ip: string, optional
        default in settings, IP where is MongoDB running
    port: interger, optional
        default in settings, port where is MongoDB running
    """

    from bson.objectid import ObjectId

    log.debug("Looking in {0} database, {1} collection under ObjectID: {2}".format(dbName, collection, idOfO))

    if type(idOfO) == str:
        idOfO = ObjectId(idOfO)

    client = MongoClient(ip, port)
    db = client[dbName][collection]

    outData = db.find_one({'_id': idOfO}, {"_id": 0})

    client.close()

    return outData


def get_id_of_last_inserted(dbName=lset.DB_NAME, collection=lset.DB_COLLECTION,
                            ip=lset.DB_IP, port=lset.DB_PORT):
    """Get ObjectID of last inserted document
    from pymongo import MongoClient

    Parameters
    ----------
    dbName: string, optional
        default in settings, name of database to write into
    collection: string, optional
        default in settings, Name of collection to write into
    ip: string, optional
        default in settings, IP where is MongoDB running
    port: interger, optional
        default in settings, port where is MongoDB running

    Returns
    -------
    ObjectID : ObjectID
        last inserted document to collection
    """

    log.debug("Looking in {0} database, {1} collection for last item.".format(dbName, collection))
    client = MongoClient(ip, port)
    db = client[dbName][collection]

    return db.find().sort('_id', -1)[0]["_id"]


def update_db_object(finder, key, value, dbName=lset.DB_NAME, collection=lset.DB_COLLECTION,
                     ip=lset.DB_IP, port=lset.DB_PORT):
    """Update object in db

    Parameters
    -----------
    finder : dict
        by which we should find {key : value}
    key: string
        under this name value will be added
    value: dict, somthing seriazable
        data to add under key
    dbName: string, optional
        default in settings, name of database to write into
    collection: string, optional
        default in settings, Name of collection to write into
    ip: string, optional
        default in settings, IP where is MongoDB running
    port: interger, optional
        default in settings, port where is MongoDB running

    Returns
    -------
    ObjectID
        of insterted document
    """
    client = MongoClient(ip, port)
    db = client[dbName][collection]

    res = db.update(finder, {"$set": {key: value}})
    return res


def find_objects_by_origurl(origUrl, dbName=lset.DB_NAME, collection=lset.DB_COLLECTION,
                            ip=lset.DB_IP, port=lset.DB_PORT):
    """Try to find object by original URL of feed and returns the LAST one inserted

    Parameters
    ----------
    origUrl : string of URL
        URL by which we should find in database
    dbName: string, optional
        default in settings, name of database to write into
    collection: string, optional
        default in settings, Name of collection to write into
    ip: string, optional
        default in settings, IP where is MongoDB running
    port: interger, optional
        default in settings, port where is MongoDB running

    Returns
    -------
    ObjectID
        of last inserted matching document

    Raises
    ------
    IndexError
        When no document is found
    """

    client = MongoClient(ip, port)
    db = client[dbName][collection]

    try:
        allRes = db.find({"origURL": origUrl}).sort('_id', -1)
        res = allRes[0]["_id"]
    except IndexError:
        res = None
    log.debug("Looking in {0} database, {1} collection for URL: {2}".format(dbName, collection, origUrl))
    # TODO: Slow! But after find is fetched by res, allRes is empty...
    #informer("Object(s) by URL found: ", [(obj["_id"], obj["_id"].generation_time.isoformat())
    #                                      for obj in db.find({"origURL": origUrl}).sort('_id', -1)])
    return res

def get_webdriver(browser):
    """Initialize the webdriver

    Parameters
    ------------
    browser: string, optinal

        Defaults to settings.DEFAULT_DRIVER

        One of ["firefox", "firefoxTOR", "phatnomjs", "phantomjsTOR", "chromium"]

        Specify which browser you want to use for scrapping and if you want
        to use TOR version or not (TOR must be running at localhost:9050, socks5!)
    """
    from selenium import webdriver

    if browser == "phantomjs":
        from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
        user_agent = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"
        )
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = user_agent
        dcap['phantomjs.page.settings.resourceTimeout'] = 60000

        _service_args = ['--load-images=no', "--webdriver-loglevel=ERROR"]
        wdriver = webdriver.PhantomJS(service_args=_service_args, service_log_path='/tmp/ghostdriver.log', desired_capabilities=dcap)

    elif browser == "phantomjsTOR":
        serviceArgs = ['--proxy=localhost:9050', '--proxy-type=socks5']
        wdriver = webdriver.PhantomJS(service_args=serviceArgs)
    elif browser == "firefox":
        from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
        firefoxProfile = FirefoxProfile()
        firefoxProfile.set_preference('permissions.default.image', 2)
        wdriver = webdriver.Firefox(firefox_profile=firefoxProfile)
    elif browser == "chromium":
        wdriver = webdriver.Chrome('chromedriver')
    elif browser == "firefoxTOR":
        profile = webdriver.FirefoxProfile()
        profile.set_preference('network.proxy.type', 1)
        profile.set_preference('network.proxy.socks', 'localhost')
        profile.set_preference('network.proxy.socks_port', 9050)
        wdriver = webdriver.Firefox(profile)

    wdriver.set_window_size(1366, 768)
    wdriver.set_page_load_timeout(30)
    return wdriver

def scraper_prep(scraper_name, webdriver):

    from collects.maternalSite import Websiteout, Urlm, RankerDist, Alexa
    scrapers = {"websiteout": (Websiteout, "www.websiteoutlook.com"),
                      "urlm": (Urlm, "www.urlm.co"),
                      "ranks": (RankerDist, "www.google.com"),
                      "alexa": (Alexa, "www.alexa.com/siteinfo")
                      }
    cls, baseurl = scrapers[scraper_name]
    return cls(baseurl, webdriver)