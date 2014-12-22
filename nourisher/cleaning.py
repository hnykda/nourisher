'''
Created on Dec 22, 2014

@author: dan
'''

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
    from locale import setlocale, LC_ALL, atof
    setlocale( LC_ALL, "en_US.UTF8" )


    if type( vst ) == float or type( vst ) == int:
        vysl = vst
    elif type( vst ) == type( None ):
        vysl = None
    elif vst.isdigit():
        vysl = atof( vst )
    elif len( vst ) > 0:
        numb = vst

        # percents to [0,1]
        if numb[-1] == "%":
            vysl = atof( numb[:-1] ) / 100

        elif numb[0] == r"$":
            if 'Million' in numb:
                spl = numb.split( " " )
                vysl = atof( spl[0][1:] ) * 1000000
            else:
                vysl = atof( numb[1:] )

        # some webs return slash when no information are provided
        elif numb == "-" or numb == "--":
            vysl = None

        # the rest should work normally - this will give errors
        else:
            vysl = atof( numb )

            # try:
            #    vysl = atof(numb)
            # except:
            #    vysl = None

    elif vst == "" or vst == []:
        vysl = None

    return( vysl )

def time_to_dec( time ):
    from locale import setlocale, LC_ALL, atof
    setlocale( LC_ALL, "en_US.UTF8" )
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

def numbs_from_list( diction, keys ):

    new = {}
    for key in keys:
        new[key] = wrangle_numbers( diction[key] )

    return( new )

def check_if_presents_list( diction, keys ):

    new = {}
    for key in keys:
        val = diction[key]
        if val == None or val == [] or val == "" or val == () or val == {}:
            new[key] = False
        else:
            new[key] = True

    return( new )

def wrangle_entries( entries ):

    newE = {}

    # little hack
    entries["summariesLength"] = [len( i.split() ) for i in entries["summaries"]]
    entries["titlesLength"] = [len( i.split() ) for i in entries["titles"]]

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

    from statistics import stdev, mean
    for key in numericLists:
        try:
            x = entries[key]
            standardDev = stdev( x )
            meanOfAll = mean( x )
        except TypeError:
            standardDev, meanOfAll = None, None

        newE[key + "_STD"], newE[key + "_MEAN"] = standardDev, meanOfAll


    countE = len( entries["finalUrl"] )
    newE.update( {"difAuthorsPerEntry" : len( set( entries["authors"] ) ) / countE} )

    return( newE )

def clean_websiteout( websData ):

    wanted_numeric = ['pageviewsPerDay', 'backlingsYahoo', 'pageRank', 'dailyUSD', 'estimatedWorth', 'websiteoutRank', 'traficRank']
    # wanted_text = ['link']

    newData = {}
    # newData.update( {'link' : websData['link']} )
    newData.update( numbs_from_list( websData, wanted_numeric ) )

    return( newData )

def clean_alexa( alexData ):

    wanted_numeric = ['searchVisits',
                     'bounceRate',
                     'dailyPagevPerVis',
                     'totalSitesLinking',
                     'globalRank']


    newData = {}
    # newData.update( {'link' : alexData['link']} )
    newData.update( {'dailyTimeOnSite' : time_to_dec( alexData['dailyTimeOnSite'] ) } )
    newData.update( numbs_from_list( alexData, wanted_numeric ) )

    return( newData )

def clean_urlm( urlmData ):

    wanted_numeric = ['valuePerVis', 'numberOfPages', 'globalRank', 'externalLinks', 'monthlyVisits', 'monthlyPagesViewed']

    newData = {}
    # newData.update( {'link' : urlmData['link']} )
    newData.update( numbs_from_list( urlmData, wanted_numeric ) )

    return( newData )

def clean_ranks( ranksData ):
    # wanted_numeric = ['r_mozrank', 'r_seznam', 'r_plusone_g', 'r_compete', 'r_alexa',
    #                  'r_twitter', 'r_majestic', 'r_google', 'r_facebook', 'r_site_explorer', 'r_jyxo']
    wanted_numeric = ['rGoogle',
         'rAlexa',
         'rCompete',
         'rMozrank',
         'rSeznam',
         'rJyxo',
         'rMajestic',
         'rSiteExplorer',
         'rFacebook',
         'rTwitter',
         'rPlusoneG'
         ]

    newData = {}
    newData.update( numbs_from_list( ranksData, wanted_numeric ) )

    return( newData )


def clean_feedInfo( feedData ):

    newData = {}

    wantedAsTheyAre = ["bozo", "pub_freq"]
    for key in wantedAsTheyAre:
        newData[key] = feedData[key]

    wantedIsPresent = ["language", "author", "tags", "subtitle", 'published_parsed', "info"]
    newData.update( check_if_presents_list( feedData, wantedIsPresent ) )

    ### MAPING ###
    fMap = lambda mapDict, x: mapDict[x]
    # 0 (zero) is for others
    mappingVersion = {'rss20': 4, 'atom10': 1, 'atom03': 4, 'rss091u': 2, 'rss10': 3}
    mappingStatus = {200: 1, 301: 2, 302: 3}

    for d, k in zip( [mappingStatus, mappingVersion], ["status", "version"] ):
        try:
            newData[k] = fMap( d, feedData[k] )
        except KeyError:
            newData[k] = 0

    entries = wrangle_entries( feedData["entries"] )
    newData.update( entries )

    return( newData )

def clean_that_all( rawData ):

    doms = ['urlm', 'websiteout', 'alexa', 'feedInfo', 'ranks']
    funcs = [clean_urlm, clean_websiteout, clean_alexa, clean_feedInfo, clean_ranks]

    # prepro = [func( rawData[dom] ) for func, dom in zip( funcs, doms ) if (rawData[dom] != None) else None]

    prepro = []
    for func, dom in zip( funcs, doms ):
        dataDomain = rawData[dom]
        if dataDomain == None:
            prepro.append( {dom : None} )
        else:
            prepro.append( func( dataDomain ) )

    cleaned = {}
    for diction in prepro:
        cleaned.update( dict( diction.items() ) )

    return( cleaned )
