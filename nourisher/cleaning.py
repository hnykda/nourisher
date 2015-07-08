"""
Created on Dec 22, 2014

@author: dan
"""
from nourisher import utiliser


def wrangle_numbers(vst):
    """ Converts string to numbers, if possible.

    Parameters
    ----------
    vst: string
        in several forms - these that are collected by scrapers

    Returns
    -------
    float
        wrangled number

    Note
    -----
    It will probably give some errors, but they can be handled
    by IFs (better for debugging)
    """
    from locale import setlocale, LC_ALL, atof

    setlocale(LC_ALL, "en_US.UTF8")

    if type(vst) == float or type(vst) == int:
        vysl = vst
    elif vst is None:
        vysl = None
    elif vst.isdigit():
        vysl = atof(vst)
    elif len(vst) > 0:
        numb = vst

        # percents to [0,1]
        if numb[-1] == "%":
            vysl = atof(numb[:-1]) / 100

        # websiteout and urlm worth
        elif ("Million" in numb) or ("Billion" in numb):

            # urlm
            if numb[1] == r"$":
                numb = numb[1:-1]

            if 'Million' in numb:
                spl = numb.split(" ")
                vysl = atof(spl[0]) * 1000000
            if "Billion" in numb:
                spl = numb.split(" ")
                vysl = atof(spl[0]) * 1000000000
        # some webs return slash when no information are provided

        elif numb[0] == r"$":
            vysl = atof(numb[1:])

        elif numb == "-" or numb == "--":
            vysl = None

        # urlm sometimes throws e.g. "< 300"
        elif numb[0] == "<":
            vysl = atof(numb[1:])
        else:
            vysl = atof(numb)

    elif vst == "" or vst == []:
        vysl = None

    utiliser.informer("Wrangling from: " + str(vst) + " to:\t " + str(vysl), level=2)
    return vysl


def time_to_dec(time):
    """Convert time interval from MM:SS to MM.S

    Parameters
    ----------
    string of time
        time in MM:SS format

    Returns
    -------
        time in minutes in decimal format
    """

    from locale import setlocale, LC_ALL, atof

    setlocale(LC_ALL, "en_US.UTF8")
    try:
        t = time

        # no information provided
        if t == "-":
            return None

        pl = t.split(":")
        minutes = atof(pl[0])
        secs = (atof(pl[1]) / 60)
        ttime = minutes + secs
        return ttime

    except:
        return None


def numbs_from_list(diction, keys):
    """Tries to wrangle every string from list to numbers"""

    utiliser.informer("Finding {0} in {1}".format(list(diction.keys()), keys), level=2)
    new = {}
    for key in keys:
        new[key] = wrangle_numbers(diction[key])

    return new


def check_if_presents_list(diction, keys):
    """Returns True if element from key is present and nonempty in diction

    Parameters
    ----------
    diction : dict
        dictionary which should be checked
    keys : list of strings
        strings that should be as keys in diction

    Returns
    -------
    dict
        in form {key:bool, ...}
    """

    new = {}
    for key in keys:
        val = diction[key]
        if val is not None or val == [] or val == "" or val == () or val == {}:
            new[key] = False
        else:
            new[key] = True

    return new


def wrangle_entries(entries):
    """Wrangle informations from entries, basically make numbers from them

    Parameters
    ----------
    entries : dict
        of information about entries which are collected by feedInfo collector

    Returns
    -------
    dict
        wrangled informations about entries for the feed
    """

    newE = {}

    # little hack
    entries["summariesLength"] = [len(i.split()) for i in entries["summaries"]]
    entries["titlesLength"] = [len(i.split()) for i in entries["titles"]]

    numericLists = ['summariesLength',
                    'titlesLength',
                    'urlCountDash',
                    'htmlCodeLengthwhite',
                    'textHtmlArticleRatioWords',
                    'urlCountHash',
                    'nTagCountsEntries_img',
                    'textHtmlArticleRatioChars',
                    'nTagCountsWhole_div',
                    'matchUrlTitle',
                    'nTagCountsWhole_meta',
                    'urlAllWeirds',
                    'nTagCountsWhole_img',
                    'textCodeHtmlRatioWT',
                    'nOfAllTagsHtml',
                    'nTagCountsEntries_div',
                    'nTagCountsWhole_iframe',
                    'nTagCountsWhole_script',
                    'nTagCountsWhole_p',
                    'uppercaseTextRatio',
                    'nTagCountsEntries_p',
                    'htmlCodeLengthChars']

    from statistics import stdev, mean, StatisticsError
    # take only those which are contained in entries keys
    for key in [att for att in numericLists if att in entries.keys()]:
        # cleaning from None values
        x = [val for val in entries[key] if val is not None]
        if len(x) > 0:
            try:
                standardDev = stdev(x)
                meanOfAll = mean(x)
            except StatisticsError:
                standardDev, meanOfAll = None, None
                utiliser.informer("array is: " + str(entries[key]))
        elif len(x) == 0:
            standardDev, meanOfAll = None, None
            utiliser.informer(r"array is empty or full of None ==" + str(entries[key]), level=2)

        newE[key + "_STD"], newE[key + "_MEAN"] = standardDev, meanOfAll

    countE = len(entries["finalUrl"])
    newE.update({"difAuthorsPerEntry": len(set(entries["authors"])) / countE})

    return newE


def clean_websiteout(websData):
    """Cleaner for websiteoutlook.com"""

    wanted_numeric = ['pageviewsPerDay', 'backlingsYahoo', 'pageRank',
                      'dailyUSD', 'estimatedWorth', 'websiteoutRank', 'traficRank']
    # wanted_text = ['link']

    newData = {}
    # newData.update( {'link' : websData['link']} )
    newData.update(numbs_from_list(websData, wanted_numeric))

    return newData


def clean_alexa(alexData):
    """Cleaner for alexa.com"""

    wanted_numeric = ['searchVisits',
                      'bounceRate',
                      'dailyPagevPerVis',
                      'totalSitesLinking',
                      'rAlexa']

    newData = {}
    # newData.update( {'link' : alexData['link']} )
    newData.update({'dailyTimeOnSite': time_to_dec(alexData['dailyTimeOnSite'])})
    newData.update(numbs_from_list(alexData, wanted_numeric))

    return newData


def clean_urlm(urlmData):
    """Cleaner for urlm.co"""

    wanted_numeric = ['valuePerVis', 'numberOfPages',
                      'globalRank', 'externalLinks', 'monthlyVisits', 'monthlyPagesViewed']

    newData = {}
    # newData.update( {'link' : urlmData['link']} )
    newData.update(numbs_from_list(urlmData, wanted_numeric))

    return newData


def clean_ranks(ranksData):
    """Cleaner for ranks"""

    wanted_numeric = ['rGoogle',
                      #'rAlexa',
                      'rCompete',
                      'rMozrank',
                      'rSeznam',
                      'rJyxo',
                      'rMajestic',
                      'rBacklingsG'
                      'rSiteExplorer',
                      'rFacebook',
                      'rTwitter',
                      #'rPlusoneG'
                      ]

    newData = {}
    newData.update(numbs_from_list(ranksData, wanted_numeric))

    return newData


def clean_feedInfo(feedData):
    """Cleaner for feed info"""

    newData = {}

    wantedAsTheyAre = ["bozo", "pub_freq"]
    for key in wantedAsTheyAre:
        newData[key] = feedData[key]

    wantedIsPresent = ["language", "author", "tags", "subtitle", 'published_parsed', "info"]
    newData.update(check_if_presents_list(feedData, wantedIsPresent))

    # MAPING ###
    fMap = lambda mapDict, x: mapDict[x]
    # 0 (zero) is for others
    mappingVersion = {'rss20': 4, 'atom10': 1, 'atom03': 4, 'rss091u': 2, 'rss10': 3}
    mappingStatus = {200: 1, 301: 2, 302: 3}

    for d, k in zip([mappingStatus, mappingVersion], ["status", "version"]):
        try:
            newData[k] = fMap(d, feedData[k])
        except KeyError:
            newData[k] = 0

    if feedData["n_of_entries"] > 0:
        entries = wrangle_entries(feedData["entries"])
        newData.update(entries)
        newData.update({"entries": True})
    elif feedData["n_of_entries"] == 0:
        newData.update({"entries": False})
    return newData


def clean_that_all(rawData):
    """Wrapper for all cleaners"""

    doms = ['urlm', 'websiteout', 'alexa', 'feedInfo', 'ranks']
    funcs = [clean_urlm, clean_websiteout, clean_alexa, clean_feedInfo, clean_ranks]

    prepro = []
    for func, dom in zip(funcs, doms):
        dataDomain = rawData[dom]
        if dataDomain is None:
            # False if there are no data available for this domain
            # and True if data were provided
            prepro.append({dom: False})
        else:
            prepro.append(func(dataDomain))
            prepro.append({dom: True})

    cleaned = {}
    for diction in prepro:
        cleaned.update(dict(diction.items()))

    return cleaned
