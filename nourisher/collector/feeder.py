import pandas as pd
import feedparser
from collections import defaultdict

# atributy, co mě u feedu zajímají
# prvni uroven feedparser objectu, bozo je je kvalita formátování feedu
iafl = [ "version", "status", "bozo", "href"]
# entries, frequence nejak nadefinovat
iae = ["n_of_entries", "freq"]
# feed uroven
iaf = ["title", "subtitle", "info",
        "language", "link", "author",
        "published_parsed", "updated_parsed", "tags"]


def extract_entries_info( entries, n_of_entries ):
    """Vrati kolik clanku dava feed za jeden den"""

    published_times = [pd.to_datetime( entry["published"] ) for entry in entries]
    pub_t = pd.TimeSeries( published_times )
    pub_freq = ( pub_t.max() - pub_t.min() ) / n_of_entries
    return( ( 24 * 3600 ) / pub_freq.total_seconds() )

def extract_feed_info( url ):
    d = feedparser.parse( url )
    ifs = {}
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
        ifs["pub_freq"] = extract_entries_info( entries, n_of_entries )
    except:
        ifs["pub_freq"] = None

    try:
        ifs["tags"] = [i["term"] for i in ifs["tags"]]
    except:
        ifs["tags"] = None

    # save whole feedparser object
    ifs["entries"] = d["entries"]
    return( pd.Series( ifs ) )

# Omezujeme se jen na prvni 25 clanku
def vytahni_info_clanku( lc ):
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
              "tagsOfEntries" : "tags"
            }
    for clanek in lc:
        for key, val in chtene.items():
            try:
                d[key].append( clanek[val] )
            except:
                d[key] = []

    return( pd.Series( d ) )


def check_similarity( entriesInfo ):
    """Zjistuje, zda se url shoduje s title clanku
    je tam primitivni ucelova funkce (delsi slova prispeji vice)
    jeste navic zjisti, zda url adresa obsahuje specialni znaky
    
    Parameters
    -----------
    Zere Panda serii, kterou vyhazuje funkce vytahni_info_clanku()
    
    """

    import re
    import numpy as np
    from difflib import SequenceMatcher

    check_let = lambda x: True if x.isalpha() == True else False
    docas_opr = pd.DataFrame( columns = ["matchUrlTitle_Mean", "matchUrlTitle_Std",
                                  "urlCountDash_mean", "urlCountDash_std", "urlCountHash_mean", "urlCountHash_std",
                                  "urlAllWeirds_mean", "urlAllWeirds_std"] )
    # for ix, links in df.final_url.items():
    corespTitles = entriesInfo.titles
    links = entriesInfo.links
    artMath = []
    d = defaultdict( list )

    for title, link in zip( corespTitles, links ):
        lsp = " ".join( link.split( "/" )[3:] )
        title = title.lower()
        hled = re.split( '_|/|-|\+', lsp.lower() )
        hled = list( filter( check_let, hled ) )
        # print(title, lsp, hled)
        # zjistim, zda je nebo neni obsazeno kazde slovo

        rat = SequenceMatcher( None, title, " ".join( hled ) ).ratio()

        # print("Hledam: ", " ".join(hled), "\t", title, "\t", rat)
        artMath.append( rat )


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
            d[dk].append( dv )

    mns, std = np.mean( artMath ), np.std( artMath )

    tores = [mns, std, normCountDash, normCountHash, normAllWeirds]
    ntor = ["matchUrlTitle_Mean", "matchUrlTitle_Std", "urlCountDash", "urlCountHash", "urlAllWeirds"]
    cd_m, cd_s = np.mean( d["urlCountDash"] ), np.std( d["urlCountDash"] )
    ch_m, ch_s = np.mean( d["urlCountHash"] ), np.std( d["urlCountHash"] )
    aw_m, aw_s = np.mean( d["urlAllWeirds"] ), np.std( d["urlAllWeirds"] )
    return( [mns, std, cd_m, cd_s, ch_m, ch_s, aw_m, aw_s] )

def feed_that_all( url ):
    '''This collect everything from above
    '''

    defaultInfo = extract_feed_info( url )

    return( defaultInfo )

