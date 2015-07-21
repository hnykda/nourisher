import logging
log = logging.getLogger(__name__)

from collections import defaultdict
from settings import ARTICLES_LIMIT


def publication_frequency(publishedTimes):
    """Frequency of publication
    
    Returns how many entries are published per one hour
    
    Parameters
    ----------
    publishedTimes : list
         Timetuples which represents publish times of articles
    
    Returns
    -------
    float
        Number of entries per hour
    """

    if type(publishedTimes) == float:
        # when just one article is there
        return None
    if len(publishedTimes) <= 1:
        return None

    from time import mktime, struct_time

    _times = publishedTimes
    times = [mktime(struct_time(x)) for x in _times if x is not None]
    if len(times) <= 1:
        return None
    first = min(times)
    last = max(times)
    # number of entries per hour
    try:
        pub_freq = len(times) / ((last - first) / 3600)
    except ZeroDivisionError:
        return None
    return pub_freq


def extract_feed_info(url):
    """Collects basic informations about the feed
    
    Parameters
    ----------
    url : string
        url of feed
    
    Returns
    -------
    dict
        dictionary with data
        
    Note
    -----
    
    TODO: except should have exceptions specified!
    
    """

    from datetime import datetime
    import feedparser

    d = feedparser.parse(url)

    ifs = {"feedparsingTime": tuple(datetime.now().timetuple())}

    # when we started parsing?

    # atributy, co mě u feedu zajímají
    # prvni uroven feedparser objectu, bozo je je kvalita formátování feedu
    iafl = ["version", "status", "bozo", "href"]
    # feed uroven
    iaf = ["title", "subtitle", "info",
           "language", "link", "author",
           "published_parsed", "updated_parsed", "tags"]

    for att in iaf:
        try:
            atrib = d.feed[att]
            if atrib != "":
                ifs[att] = atrib
            else:
                ifs[att] = None
        except KeyError:
            ifs[att] = None

    for att in iafl:
        try:
            atrib = d[att]
            if atrib != "":
                ifs[att] = atrib
            else:
                ifs[att] = None
        except:
            ifs[att] = None

    try:
        entries = d["entries"]
        n_of_entries = len(entries)
        ifs["n_of_entries"] = n_of_entries
    except:
        ifs["n_of_entries"] = None

    try:
        ifs["pub_freq"] = publication_frequency([tuple(i["published_parsed"]) for i in entries])
    except:
        ifs["pub_freq"] = None

    try:
        ifs["tags"] = [i["term"] for i in ifs["tags"]]
    except:
        ifs["tags"] = None

    # save whole feedparser object
    ifs["entries"] = d["entries"]

    return dict(ifs)


# TODO: polish_entries_info, get_entries_info should be somehow joined
# maybe called by extract_feed_info directly

# Omezujeme se jen na prvni 25 clanku
def polish_entries_info(lc):
    """Get informations about entries of the feed

    TODO: Should be better implemented inside e.g. extract feed info

    Parameters
    ----------
    lc : dict
        dict of entries
        ODO: Not sure what this is...

    Returns
    -------
    dict
        dict with polished informations

    Note
    -----
    TODO: First or last?

    **Alert!** Only first/last 25 entries are being considered

    TODO: except should have exceptions specified!
    """
    if len(lc) > 25:
        lc = lc[:25]
    d = defaultdict(list)
    chtene = {"authors": "author",
              "links": "link",
              "titles": "title",
              "summaries": "summary",
              "tagsOfEntries": "tags",
              "publishedParsed": "published_parsed",
              "updatedParsed": "updated_parsed",
              "baseHtmls": "base"
              }
    for clanek in lc:
        for key, val in chtene.items():
            try:
                d[key].append(clanek[val])
            except:
                d[key] = []

    return dict(d)


def get_entries_info(links):
    """ Collect all informations about entries as a list

    TODO: Viz TODO nad polished_entries...

    TODO: This could be definitely made better - not just one enormous try block

    Parameters
    -----------
    links: list
        list of links

    Returns
    -------
    dict
        Parsed information about entries


    """

    import newspaper as nwsp
    from bs4 import BeautifulSoup
    from lxml.etree import tostring
    import requests

    dtb = defaultdict(list)

    log.debug("Parsing links... ")

    # just for process checking
    counterI = 1
    for plink in links[:ARTICLES_LIMIT]:
        # TODO: This is wrong - values are now mixed (not that anybody cares...)
        try:
            # this is because requests follow redirects,
            # hence it ends up on true address
            artURL = requests.get(plink).url
            dtb["finalUrl"].append(artURL)
            log.debug("Parsing link {0}/{1}: ".format(counterI, len(links)) + str(artURL), level=1,
                              rewrite=True)
            counterI += 1

            art = nwsp.Article(artURL)
            art.download()
            art.parse()

            dtb["sourceURL"].append(art.source_url)

            #art.nlp()
            #dtb["articleKeywords"].append( art.keywords )

            dtb["guessed_language"].append( art.extractor.language )

            dtb["count_images"].append( art.imgs )

            pageHtml = art.html
            pageSoup = BeautifulSoup(pageHtml)
            strSoup = str(pageSoup)
            strSoupSplit = strSoup.split()

            # length of code in chars normed to text
            dtb["htmlCodeLengthChars"].append(len(strSoup))
            # length of code splitted at whitespace
            dtb["htmlCodeLengthwhite"].append(len(strSoupSplit))

            # count all tags
            dtb["nOfAllTagsHtml"].append(len(pageSoup.findAll()))

            wanted_tags = ["meta", "script", "iframe", "div", "img", "p"]
            for tag in wanted_tags:
                nm = "nTagCountsWhole_" + tag
                poc = len(pageSoup.findAll(tag))
                dtb[nm].append(poc)

            # get text of an article
            artText = art.text
            if artText == '':
                artText = None
            dtb["text"].append(artText)

            # counts number of specific tags in the article html code
            try:
                artHtm = tostring(art.top_node)
                dtb["htmlText"].append(artHtm.decode())
                artSoup = BeautifulSoup(artHtm)
                chtene = ["img", "div", "p"]
                for tag in chtene:
                    nm = "nTagCountsEntries_" + tag
                    poc = len(artSoup.findAll(tag))
                    dtb[nm].append(poc)

                # ratio length in characters of text vs. html code of the article
                rat = len(artText) / len(artHtm)
                dtb["textHtmlArticleRatioChars"].append(rat)

                # ratio number of words vs number of tags in an article
                # this is IMHO better than characters, since tags can have long names
                # or css styling attributes
                ratW = len(artText.split()) / len(artSoup.findAll())
                dtb["textHtmlArticleRatioWords"].append(ratW)

                # text words vs. number of tags
                ratWT = len(artText.split()) / len(pageSoup.findAll())
                dtb["textCodeHtmlRatioWT"].append(ratWT)

                # number of uppercase letters vs words ratio
                ratUT = sum(1 for letter in artText if letter.isupper()) / len(strSoupSplit)
                dtb["uppercaseTextRatio"].append(ratUT)

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
                    dtb[notAble].append(None)

                    # Not needed
                    # dtb["rawHtmlOfPage"].append( str( pageSoup ) )

        except (
                TypeError, nwsp.article.ArticleException, UnicodeDecodeError,
                requests.exceptions.ConnectionError) as ex:
            import traceback

            log.warning("\nError when parsing an article", ex)
            print(traceback.format_exc())
    # utiliser.informer( "Parsed articles: ", dtb['finalUrl'], level = 2 )
    log.debug("Number of parsed articles: {0}".format(len(dtb['finalUrl'])))
    return dict(dtb)


def get_url_info(links, corespTitles):
    """Zjistuje, zda se url shoduje s title clanku
    je tam primitivni ucelova funkce (delsi slova prispeji vice)
    jeste navic zjisti, zda url adresa obsahuje specialni znaky
    
    Parameters
    -----------
    links : list 
        corresponding links of titles
    corespTitles: list 
        corresponding titles to links

    Returns
    -------
    dict
        dictionary with informations
    
    Note
    -----
    Links comes from true end address where they were parsered by newspaper, 
    not from the original feed.
    """

    import re
    from difflib import SequenceMatcher

    check_let = lambda x: True if x.isalpha() is True else False

    storeD = defaultdict(list)

    for title, link in zip(corespTitles, links):
        lsp = " ".join(link.split("/")[3:])
        title = title.lower()
        hled = re.split('_|/|-|\+', lsp.lower())
        hled = list(filter(check_let, hled))

        rat = SequenceMatcher(None, title, " ".join(hled)).ratio()

        storeD["matchUrlTitle"].append(rat)

        # weird occurences vs textual
        numbAndWeird = re.findall("[\W|\d]+", lsp)
        countDash = len(list(filter(lambda x: True if x == "-"else False, numbAndWeird)))
        try:
            normCountDash = countDash / len(hled)
        except ZeroDivisionError:
            normCountDash = 0

        countHash = len(list(filter(lambda x: True if "#" in x else False, numbAndWeird)))
        try:
            normCountHash = countHash / len(hled)
        except ZeroDivisionError:
            normCountHash = 0

        allWe = list(filter(lambda x: True if (("-" != x) or ("/" != x)) else False, numbAndWeird))
        countAllWeirds = len(allWe)
        try:
            normAllWeirds = countAllWeirds / len(hled)
        except ZeroDivisionError:
            normAllWeirds = 0

        for dk, dv in zip(["urlCountDash", "urlCountHash", "urlAllWeirds"],
                          [normCountDash, normCountHash, normAllWeirds]):
            storeD[dk].append(dv)

    return dict(storeD)


def feed_that_all(url):
    """This collect everything from above

    Parameters
    ----------
    url : string
        URL of feed

    Returns
    -------
    dict
        all data collected by feeder
    list
        list of URL addresses which will alexa use to try to find maternal URL
    """

    defaultInfo = extract_feed_info(url)

    if defaultInfo["n_of_entries"] > 0:
        entriesPolished = polish_entries_info(defaultInfo["entries"])
        entrieInfo = get_entries_info(entriesPolished["links"])
        entriesSim = get_url_info(entrieInfo["finalUrl"], entriesPolished["titles"])

        entriesTotal = {}
        for diction in [entriesPolished, entrieInfo, entriesSim]:
            entriesTotal.update(diction)

        # for finding maternalURL
        finalUrls = entrieInfo["finalUrl"]
    elif defaultInfo["n_of_entries"] == 0:
        log.error("No entries have been found!")
        entriesTotal = None
        # nothing else to do...
        finalUrls = [defaultInfo["href"]]

    # feedparser object of entries is no longer needed
    defaultInfo.pop("entries")

    # thanks to mongo we do not fear structured data
    total = {}
    total.update(defaultInfo)
    total.update({"entries": entriesTotal})

    return total, finalUrls
