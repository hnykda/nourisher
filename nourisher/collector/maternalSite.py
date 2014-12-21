from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

class Scraper:
    ''' This is common interface for all scrapers, 
    like these for Alexa.com, urlm.com, websiteoutlook.com, etc.
    
    There should not be any wrangling - save it as it is somewhere and
    after that wrangling can come - there might be errors during it and
    it is inconvenient to collect data again if they are corrupted.
        
    Atributes
    ---------
    baseURL: URL address without http:// of the webpage from which data should
    be scraped of
    maternalURL: URL of maternal website of feed we want to get info about
    textWantedSingle: Dict in format {nameOfAttribut : xpathOfAttribut}, 
    those atts we want text from and it's a single value 
    textWanteddouble: Dict in format {nameOfCollection : (keys : vals )}, these
    are pairs columns (e.g. tables) from which we want to extract text 
    scrapedData: All data which were scraped
    '''

    baseURL = ""
    maternalURL = ""
    scrapedData = None
    nameOfInputField = ""
    driver = None


    def __init__( self, _maternalURL, _baseURL, _xpathOfInputField ):
        ''' Init
        
        Parameters
        ----------
        _xpathOfInputField: name of field where is the input field for
        maternal URL
        '''

        self.baseURL = _baseURL
        # self.textWantedSingle = _textWantedSingle

        # if _textWantedDouble != None:
            # self.textWantedDouble = _textWantedDouble

        wdriver = webdriver.PhantomJS()
        # wdriver = webdriver.Firefox()
        wdriver.get( r'http://' + _baseURL )
        inputField = wdriver.find_element_by_xpath( _xpathOfInputField )
        inputField.clear()
        inputField.send_keys( _maternalURL )
        inputField.submit()

        # what happens if no informations are provided


        # TODO: get printscreen of that page and save it

        self.driver = wdriver

    def selxs( self, xpath ):
        '''this is just shortage for finding ALL matching fields'''

        elems = self.driver.find_elements_by_xpath( xpath )
        res = [value.text for value in elems]

        return( res )

    def selx( self, xpath ):
        '''this is just shortage for finding ONE matching fields'''

        try:
            res = self.driver.find_element_by_xpath( xpath ).text
        except NoSuchElementException:
            res = None

        return( res )

    def collect_textual_singles( self, textWantedSingle ):
        '''Collects all text from items in textWantedSingle
        
        Returns
        -------
        dict in format {nameOfAtt, value}
        '''

        xitems = {}
        for name, xpath in textWantedSingle.items():
            xitems[name] = self.selx( xpath )


        return( xitems )

    def collect_textual_singles_lists( self, textWantedSingleList ):
        '''For attributes in type key: [val1, val2, ...]'''

        xitems = {}
        for key, xpath in textWantedSingleList.items():
            xitems[key] = self.selxs( xpath )

        return( xitems )

    def _collect_two_zip( self, Axpath, Bxpath ):
        '''It's common to get data in two collumns (e.g. in tables)
        so this will return them in pandas serie
        '''
        A = self.selxs( Axpath )
        B = self.selxs( Bxpath )

        # used to be a dict, but mongodb can't store things
        # under key which contain a dot
        return( tuple( zip( A, B ) ) )

    def collect_textual_doubles( self, textWantedDouble ):
        '''Collects all text from items in textWantedDouble
        
        Returns
        -------
        dict of dicts in format {nameOfCollection : data}, where 
        data is in {nameOfVal : val} 
        '''

        xitems = {}
        for nameOfCollection, ( nameXp, valXp ) in textWantedDouble.items():
            xitems[nameOfCollection] = self._collect_two_zip( nameXp, valXp )

        return( xitems )

    def collect_that_all( self ):
        '''Collects all possible informations - every instance must implement
         
        Parameters
        ----------
        maternalURL: url of maternal website of feed
        
        Returns
        --------
        pandas-serie with data
        '''

        raise

class Alexa( Scraper ):
    ''' This holder for Alexa.com informations
    '''

    alexa_singles = {
               'link' : '//*[@id="js-li-last"]/span[1]/a',
               'globalRank' : '//*[@id="traffic-rank-content"]/div/span[2]/div[1]/span/span/div/strong',
               'globalRankChange' : '//*[@id="traffic-rank-content"]/div/span[2]/div[2]/span/span/div/strong',
               'inCountry' : '//*[@id="traffic-rank-content"]/div/span[2]/div[2]/span/span/h4/a',
               'rankInCountry' : '//*[@id="traffic-rank-content"]/div/span[2]/div[2]/span/span/div/strong',
               'bounceRate': '//*[@id="engagement-content"]/span[1]/span/span/div/strong',
               'bounceRateChange' : '//*[@id="engagement-content"]/span[1]/span/span/div/span',
               'dailyPagevPerVis' : '//*[@id="engagement-content"]/span[2]/span/span/div/strong',
               'dailyPagevPerVisChange' : '//*[@id="engagement-content"]/span[2]/span/span/div/span',
               'dailyTimeOnSite' : '//*[@id="engagement-content"]/span[3]/span/span/div/strong',
               'dailyTimeOnSiteChange' : '//*[@id="engagement-content"]/span[3]/span/span/div/span',
               'searchVisits' : '//*[@id="keyword-content"]/span[1]/span/span/div/strong',
               'searchVisitsChange' : '//*[@id="keyword-content"]/span[1]/span/span/div/span',
               'totalSitesLinking' : '//*[@id="linksin-panel-content"]/div[1]/span/div/span',
               'relatedLinks' : '//*[@id="related_link_table"]/tbody/tr/td/a',
               }

    alexa_doubles = {
               'popKeywords' : ( '//*[@id="keywords_top_keywords_table"]/tbody/tr/td[1]/span[2]',
                             '//*[@id="keywords_upstream_site_table"]/tbody/tr/td[2]/span' ),
               'upstreamSites' : ( '//*[@id="keywords_upstream_site_table"]/tbody/tr/td[1]/a',
                                  '//*[@id="keywords_upstream_site_table"]/tbody/tr/td[2]/span' ),
               'whereGoNext': ( '//*[@id="subdomain_table"]/tbody/tr/td/span[@class="word-wrap"]',
                               '//*[@id="subdomain_table"]/tbody/tr/td[@class="text-right"]/span' )
               }


    def collect_that_all( self ):

        total = {}
        singles = self.collect_textual_singles( self.alexa_singles )
        doubles = self.collect_textual_doubles( self.alexa_doubles )

        # Categories
        # TODO: temer jiste spatne, pohandlovat lepe - mozna newranglovat
        # categories = []
        # for catl in self.selx( '//*[@id="category_link_table"]/tbody/tr' ):
        #    a = catl.xpath( 'td/span/a/@href' )
        #    categories.append( a.extract()[-1] )
            # try:
            #    categories.append( a.extract()[-1] )
            # except:
            #    pass

        total.update( singles )
        total.update( doubles )
        # total.update( {"categories" : categories} )

        self.scrapedData = total

class Websiteout( Scraper ):
    ''' This is holder for Websiteoutlook.com informations
    '''

    webout_singles = {
                    "link" : '//*[@id="right"]/table[1]/tbody/tr[1]/td[2]/span/span',
                    "pageviewsPerDay" : '//*[@id="right"]/table[1]/tbody/tr[2]/td[2]',
                    "dailyUSD" : '//*[@id="right"]/table[1]/tbody/tr[3]/td[2]',
                    "websiteoutRank" : '//*[@id="right"]/table[1]/tbody/tr[4]/td[2]/span[1]',
                    "backlingsYahoo" : '//*[@id="right"]/table[2]/tbody/tr[3]/td[2]',
                    "traficRank" : '//*[@id="right"]/table[2]/tbody/tr[1]/td[2]',
                    'pageRank' : '//*[@id="right"]/table[2]/tbody/tr[2]/td[2]',
                    }

    def collect_that_all( self ):
        total = {}
        singles = self.collect_textual_singles( self.webout_singles )

        categories = self.selxs( '//*[@id="right"]/table[2]/tbody/tr[4]/td[2]/ol/li/a' )

        otherSites = self.selxs( '//*[@id="right"]/table[7]/tbody/tr[2]/td[1]/ol/li/a' )

        # estimated worth
        text = self.selxs( '//*[@id="right"]/div[3]/p' )
        splText = text[0].split()
        splText.reverse()
        iDofWorth = splText.index( "USD" )
        total.update( {'estimatedWorth' : splText[iDofWorth - 1] } )

        total.update( singles )
        total.update( {'categories' : categories} )
        total.update( {'otherSites' : otherSites} )

        self.scrapedData = total

class Urlm( Scraper ):
    '''Holder for data from Urlm.com informations'''

    # TODO: Needs a lot of polishin - specially age, category, sitesLinkingIn/Out, popPages

    urlm_singles = {
                    'link' : '/html/body/div[1]/div[2]/div/div[1]/div[1]/span',
                    'globalRank' : '//*[@id="summary"]/div[1]/p[2]/span[1]',
                    'inCountry' : '//*[@id="summary"]/div[1]/p[1]/span[2]',
                    'rankInCountry' : '//*[@id="summary"]/div[1]/p[1]/span[1]',
                    'monthlyPagesViewed' : '//*[@id="summary"]/div[2]/table/tbody/tr[1]/td[2]',
                    'monthlyVisits' : '//*[@id="summary"]/div[2]/table/tbody/tr[2]/td[2]',
                    'valuePerVis' : '//*[@id="summary"]/div[2]/table/tbody/tr[3]/td[2]',
                    'estimatedWorth' : '//*[@id="summary"]/div[2]/table/tbody/tr[4]/td[2]',
                    'externalLinks' : '//*[@id="summary"]/div[2]/table/tbody/tr[5]/td[2]',
                    'numberOfPages' : '//*[@id="summary"]/div[2]/table/tbody/tr[6]/td[2]',
                    'topics' : '//*[@id="web"]/p[1]',
                    'category' : '//*[@id="web"]/p[2]',
                    'infoPerDay' : '//*[@id="web"]/p[3]',
                    }
    urlm_singles_lists = {'sitesLinkingIn' : '//*[@id="web"]/ul[2]/li',
                          'sitesLinkingOut' : '//*[@id="web"]/ul[3]/li',
                          'popPages' : '//*[@id="web"]/ul[1]/li',
                          }

    urlm_doubles = { 'rankPerCountries' : ( '//*[@id="summary"]/div[5]/table/tr/td[1]',
                                           '//*[@id="summary"]/div[5]/table/tr/td[2]' ),
                    'average90Days' : ( '//*[@id="visitors"]/table[3]/tr/th',
                                       '//*[@id="visitors"]/table[3]/tr/td[2]' ),
                    }

    def collect_that_all( self ):
        total = {}

        singles = self.collect_textual_singles( self.urlm_singles )
        _singlesLists = self.collect_textual_singles_lists( self.urlm_singles_lists )

        # take out first rubish
        singlesLists = {}
        for key, listik in _singlesLists.items():
            singlesLists[key] = listik[1:]

        doubles = self.collect_textual_doubles( self.urlm_doubles )

        total.update( singles )
        total.update( singlesLists )
        total.update( doubles )

        self.scrapedData = total


### RANKS ###

class Ranker( Scraper ):
    '''Holder for ranks'''

    _rankNames = ['r_google',
         'r_alexa',
         'r_compete',
         'r_mozrank',
         'r_seznam',
         'r_jyxo',
         'r_backlinks_g',
         'r_majestic',
         'r_site_explorer',
         'r_facebook',
         'r_twitter',
         'r_plusone_g'
         ]

    def to_digit( self, lex_numb ):
        """Prevede rank na cislo, je-li to mozne"""
        from locale import atof
        numb = ""
        try:
            if ( lex_numb == "N/A" ):
                numb = None
            elif "/" in lex_numb:
                val = lex_numb.split( "/" )[0]
                if "-" in val:
                    numb = None
                else:
                    numb = atof( val )
            # for google backlinks
            elif ";" in lex_numb:
                numb = lex_numb
            else:
                numb = atof( lex_numb )
        except ValueError:
            # print( "Chyba prevodu: ", lex_numb, ". Vracim stejny string." )
            numb = lex_numb
        return( numb )

    def collect_that_all( self ):
        _ranks = self.selxs( '//*[@id="content"]/center/table/tbody/tr/td[2]' )
        ranks = [self.to_digit( lexNumb ) for lexNumb in _ranks]

        self.scrapedData = dict( zip( self._rankNames, ranks ) )

def collect_alexa( maternalURL ):
    alexa = Alexa( maternalURL, "www.alexa.com", '//*[@id="alx-content"]/div/div/span/form/input' )
    alexa.collect_that_all()
    return( alexa.scrapedData )

def collect_websiteout( maternalURL ):
    websiteout = Websiteout( maternalURL, "www.websiteoutlook.com", '//*[@id="header"]/form/input[1]' )
    websiteout.collect_that_all()
    return ( websiteout.scrapedData )

def collect_urlm( maternalURL ):
    urlm = Urlm( maternalURL, "www.urlm.co", '//*[@id="url"]' )
    urlm.collect_that_all()
    return( urlm.scrapedData )

def collect_ranks( maternalURL ):
    ranks = Ranker( maternalURL, "pagerank.jklir.net", '//*[@id="url"]' )
    ranks.collect_that_all()
    return( ranks.scrapedData )

def maternal_that_all( maternalURL ):
    ''' An ultimate function that will return information from all maternal scrapers
    '''

    total = {}
    total.update( {"alexa" : collect_alexa( maternalURL ) } )
    total.update( {"websiteout" : collect_websiteout( maternalURL ) } )
    total.update( {"urlm" : collect_urlm( maternalURL ) } )
    total.update( {'ranks' : collect_ranks( maternalURL ) } )

    return( total )
