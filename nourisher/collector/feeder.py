from collections import defaultdict
from nourisher import settings as setl, utiliser

def number_of_entries_per_day( published_times ):
    """Vrati kolik clanku dava feed za jeden den"""

    from time import mktime, struct_time

    _times = published_times
    times = [mktime( struct_time( x ) ) for x in _times]
    first = min( times )
    last = max( times )
    # number of entries per hour
    pub_freq = len( times ) / ( ( last - first ) / 3600 )
    return( pub_freq )


def extract_feed_info( url ):

    from datetime import datetime
    import feedparser

    d = feedparser.parse( url )

    ifs = {}

    # when we started parsing?
    ifs["feedparsingTime"] = tuple( datetime.now().timetuple() )

    # atributy, co mě u feedu zajímají
    # prvni uroven feedparser objectu, bozo je je kvalita formátování feedu
    iafl = [ "version", "status", "bozo", "href"]
    # feed uroven
    iaf = ["title", "subtitle", "info",
            "language", "link", "author",
            "published_parsed", "updated_parsed", "tags"]

    for att in iaf:
        try:
            atrib = d.feed[att]
            if ( atrib != "" ):
                ifs[att] = atrib
            else:
                ifs[att] = None
        except KeyError:
            ifs[att] = None

    for att in iafl:
        try:
            atrib = d[att]
            if ( atrib != "" ):
                ifs[att] = atrib
            else:
                ifs[att] = None
        except:
            ifs[att] = None

    try:
        entries = d["entries"]
        n_of_entries = len( entries )
        ifs["n_of_entries"] = n_of_entries
    except:
        ifs["n_of_entries"] = None

    try:
        ifs["pub_freq"] = number_of_entries_per_day( entries["published_parsed"] )
    except:
        ifs["pub_freq"] = None

    try:
        ifs["tags"] = [i["term"] for i in ifs["tags"]]
    except:
        ifs["tags"] = None

    # save whole feedparser object
    ifs["entries"] = d["entries"]


    return( dict( ifs ) )



# Omezujeme se jen na prvni 25 clanku
def polish_entries_info( lc ):
    '''Vytahne info o clancich z dictu
    
    Note
    -----
    Pozor! Jen 25 clanku!
    '''
    if len( lc ) > 25:
        lc = lc[:25]
    d = defaultdict( list )
    chtene = {"authors" : "author",
              "links" : "link",
              "titles" : "title",
              "summaries" : "summary",
              "tagsOfEntries" : "tags",
              "publishedParsed" : "published_parsed",
              "updatedParsed" : "updated_parsed",
              "baseHtmls" : "base"
            }
    for clanek in lc:
        for key, val in chtene.items():
            try:
                d[key].append( clanek[val] )
            except:
                d[key] = []

    return( dict( d ) )

def get_entries_info( links ):
    ''' Collect all informations about entries as a list
    
    Parameters
    -----------
    links: list of links
    
    Returns
    -------
    Informations about entries in lists
    
    '''

    import newspaper as nwsp
    from bs4 import BeautifulSoup
    from lxml.etree import tostring
    import requests

    dtb = defaultdict( list )

    utiliser.informer( "Parsing links... " )

    # just for process checking
    counterI = 1
    for plink in links:
        # TODO: This is wrong - values are now mixed (not that anybody cares...)
        try:
            # this is because requests follow redirects,
            # hence it ends up on true address
            artURL = requests.get( plink ).url
            dtb["finalUrl"].append( artURL )
            utiliser.informer( "Parsing link {0}/{1}: ".format( counterI, len( links ) ) + str( artURL ), level = 1, rewrite = True )
            counterI += 1

            art = nwsp.Article( artURL )
            art.download()
            art.parse()
            art.nlp()

            dtb["sourceURL"].append( art.source_url )
            dtb["articleKeywords"].append( art.keywords )

            pageHtml = art.html
            pageSoup = BeautifulSoup( pageHtml )
            strSoup = str( pageSoup )
            strSoupSplit = strSoup.split()

            # length of code in chars normed to text
            dtb["htmlCodeLengthChars"].append( len( strSoup ) )
            # length of code splitted at whitespace
            dtb["htmlCodeLengthwhite"].append( len( strSoupSplit ) )

            # count all tags
            dtb["nOfAllTagsHtml"].append( len( pageSoup.findAll() ) )

            wanted_tags = ["meta", "script", "iframe", "div", "img", "p"]
            for tag in wanted_tags:
                nm = "nTagCountsWhole_" + tag
                poc = len( pageSoup.findAll( tag ) )
                dtb[nm].append( poc )

            # get text of an article
            artText = art.text
            if artText == '':
                artText = None
            dtb["text"].append( artText )

            # counts number of specific tags in the article html code
            try:
                artHtm = tostring( art.top_node )
                dtb["htmlText"].append( artHtm )
                artSoup = BeautifulSoup( artHtm )
                chtene = ["img", "div", "p"]
                for tag in chtene:
                    nm = "nTagCountsEntries_" + tag
                    poc = len( artSoup.findAll( tag ) )
                    dtb[nm].append( poc )

                # ratio length in characters of text vs. html code of the article
                rat = len ( artText ) / len ( artHtm )
                dtb["textHtmlArticleRatioChars"].append( rat )

                # ratio number of words vs number of tags in an article
                # this is IMHO better than characters, since tags can have long names
                # or css styling attributes
                ratW = len ( artText.split() ) / len ( artSoup.findAll() )
                dtb["textHtmlArticleRatioWords"].append( ratW )

                # text words vs. number of tags
                ratWT = len ( artText.split() ) / len ( pageSoup.findAll() )
                dtb["textCodeHtmlRatioWT"].append( ratWT )

                # number of uppercase letters vs words ratio
                ratUT = sum( 1 for letter in artText if letter.isupper() ) / len( strSoupSplit )
                dtb["uppercaseTextRatio"].append( ratUT )

            # if there is no text, there is no reason why to continue
            except TypeError:
                noTextConsequence = ['htmlText',
                                     'nTagCountsEntries_div',
                                     'nTagCountsEntries_img',
                                     'nTagCountsEntries_p',
                                     'textCodeHtmlRatioWT',
                                     'textHtmlArticleRatioChars',
                                     'textHtmlArticleRatioWords',
                                     'uppercaseTextRatio',
                                     ]

                for notAble in noTextConsequence:
                    dtb[notAble].append( None )

            # Not needed
            # dtb["rawHtmlOfPage"].append( str( pageSoup ) )

        except ( TypeError, nwsp.article.ArticleException ):
            utiliser.informer( "\nError when parsing an article" )
    utiliser.informer( "Parsed articles: ", dtb['finalUrl'], level = 2 )
    utiliser.informer( "Number of parsed articles: ", len( dtb['finalUrl'] ), level = 1 )
    return( dict( dtb ) )

def get_url_info( links, corespTitles ):
    """Zjistuje, zda se url shoduje s title clanku
    je tam primitivni ucelova funkce (delsi slova prispeji vice)
    jeste navic zjisti, zda url adresa obsahuje specialni znaky
    
    Parameters
    -----------
    links: corresponding links of titles
    corespTitles: corresponding titles to links

    Note
    -----
    Links comes from true end address where they were parsered by newspaper, 
    not from the original feed
    """

    import re
#    import numpy as np
    from difflib import SequenceMatcher

    check_let = lambda x: True if x.isalpha() == True else False

    storeD = defaultdict( list )

    for title, link in zip( corespTitles, links ):
        lsp = " ".join( link.split( "/" )[3:] )
        title = title.lower()
        hled = re.split( '_|/|-|\+', lsp.lower() )
        hled = list( filter( check_let, hled ) )

        rat = SequenceMatcher( None, title, " ".join( hled ) ).ratio()

        storeD["matchUrlTitle"].append( rat )

        # weird occurences vs textual
        numbAndWeird = re.findall( "[\W|\d]+", lsp )
        countDash = len( list( filter( lambda x: True if x == "-"else False, numbAndWeird ) ) )
        try:
            normCountDash = countDash / len( hled )
        except ZeroDivisionError:
            normCountDash = 0

        countHash = len( list( filter( lambda x: True if "#" in x else False, numbAndWeird ) ) )
        try:
            normCountHash = countHash / len( hled )
        except ZeroDivisionError:
            normCountHash = 0

        allWe = list( filter( lambda x: True if ( ( "-" != x ) or ( "/" != x ) ) else False, numbAndWeird ) )
        countAllWeirds = len( allWe )
        try:
            normAllWeirds = countAllWeirds / len( hled )
        except ZeroDivisionError:
            normAllWeirds = 0

        for dk, dv in zip( ["urlCountDash", "urlCountHash", "urlAllWeirds"], [normCountDash, normCountHash, normAllWeirds] ):
            storeD[dk].append( dv )

#     mns, std = np.mean( artMath ), np.std( artMath )
#
#
#     cd_m, cd_s = np.mean( storeD["urlCountDash"] ), np.std( storeD["urlCountDash"] )
#     ch_m, ch_s = np.mean( storeD["urlCountHash"] ), np.std( storeD["urlCountHash"] )
#     aw_m, aw_s = np.mean( storeD["urlAllWeirds"] ), np.std( storeD["urlAllWeirds"] )
#
#     cols = ["matchUrlTitle_Mean", "matchUrlTitle_Std",
#              "urlCountDash_mean", "urlCountDash_std",
#              "urlCountHash_mean", "urlCountHash_std",
#              "urlAllWeirds_mean", "urlAllWeirds_std"]
#     vals = [mns, std, cd_m, cd_s, ch_m, ch_s, aw_m, aw_s]


    return( dict( storeD ) )

def feed_that_all( url ):
    '''This collect everything from above
    
    Returns
    -------
    total: all data collected by feeder
    finalURLs: list of URL addresses which will alexa use to try to find maternal URL
    '''

    defaultInfo = extract_feed_info( url )

    if defaultInfo["n_of_entries"] > 0:
        entriesPolished = polish_entries_info( defaultInfo["entries"] )
        entrieInfo = get_entries_info( entriesPolished["links"] )
        entriesSim = get_url_info( entrieInfo["finalUrl"], entriesPolished["titles"] )

        entriesTotal = {}
        for diction in [entriesPolished, entrieInfo, entriesSim]:
            entriesTotal.update( diction )

        # for finding maternalURL
        finalUrls = entrieInfo["finalUrl"]
    elif defaultInfo["n_of_entries"] == 0:
        utiliser.informer( "No entries are found!" )
        entriesTotal = None
        # nothing else to do...
        finalUrls = [defaultInfo["href"]]

    # feedparser object of entries is no longer needed
    defaultInfo.pop( "entries" )

    # thanks to mongo we do not fear structured data
    total = {}
    total.update( defaultInfo )
    total.update( {"entries" : entriesTotal } )

    return( total, finalUrls )
