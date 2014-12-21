from selenium import webdriver
from ..utiliser import wrangle_numbers
from mock import self

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
    
    Note
    ----
    TODO: xpaths could be probably be replaced by better selector
    methods, since selenium is capable of many different approaches  
        
    '''

    baseURL = ""
    maternalURL = ""
    textWantedSingle = {}
    textWantedDouble = {}
    scrapedData = None
    nameOfInputField = ""
    # this is selenium phantomJS scraper
    driver = None


    def __init__( self, _maternalURL, _baseURL, _nameOfInputField,
                 _textWantedSingle, _textWantedDouble = None ):
        ''' Init
        
        Parameters
        ----------
        _nameOfInputField: name of field where is the input field for
        maternal URL
        '''

        self.baseURL = _baseURL
        self.textWantedSingle = _textWantedSingle

        if _textWantedDouble != None:
            self.textWantedDouble = _textWantedDouble

        wdriver = webdriver.PhantomJS()
        wdriver.get( _baseURL )
        inputField = wdriver.find_element_by_name( _nameOfInputField )
        inputField.send_keys( _maternalURL )
        wdriver.submit()

        # TODO: get printscreen of that page and save it

        self.driver = wdriver

    def selxs( self, _xpath, text = True ):
        '''this is just shortage for finding ALL matching fields'''

        # TODO: not sure how this is handled in selenium
        if text == True:
            xpath = _xpath + r'/text()'
        else:
            xpath = _xpath

        return( self.driver.select_elements_by_xpath( xpath ) )

    def selx( self, _xpath, text = True ):
        '''this is just shortage for finding ONE matching fields'''
        if text == True:
            xpath = _xpath + r'/text()'
        else:
            xpath = _xpath

        return( self.driver.select_element_by_xpath( xpath ) )

    def collect_textual_singles( self ):
        '''Collects all text from items in textWantedSingle
        
        Returns
        -------
        dict in format {nameOfAtt, value}
        '''

        xitems = {}
        for name, xpath in self.textWantedSingle:
            xitems[name] = self.selx( xpath ).text


        return( xitems )


    def _collect_two_zip( self, Axpath, Bxpath ):
        '''It's common to get data in two collumns (e.g. in tables)
        so this will return them in pandas serie
        '''
        A = self.selxs( Axpath )
        B = self.selxs( Bxpath )

        return( dict( zip( A, B ) ) )

    def collect_textual_doubles( self ):
        '''Collects all text from items in textWantedDouble
        
        Returns
        -------
        dict of dicts in format {nameOfCollection : data}, where 
        data is in {nameOfVal : val} 
        '''

        xitems = {}
        for nameOfCollection, ( nameXp, valXp ) in self.textWantedDouble.items():
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

    def collect_that_all( self ):

        total = {}
        singles = self.collect_textual_singles()
        doubles = self.collect_textual_doubles()

        # Categories
        # TODO: temer jiste spatne, pohandlovat lepe - mozna newranglovat
        categories = []
        for catl in self.selx( '//*[@id="category_link_table"]/tbody/tr' ):
            a = catl.xpath( 'td/span/a/@href' )
            categories.append( a.extract()[-1] )
            # try:
            #    categories.append( a.extract()[-1] )
            # except:
            #    pass

        total.update( singles )
        total.update( doubles )
        total.update( {"categories" : categories} )

        self.scrapedData = total

class Websiteout( Scraper ):
    ''' This is holder for Websiteoutlook.com informations
    '''

    def collect_that_all( self ):
        total = {}
        singles = self.collect_textual_singles()


        # TODO: spatne! dodelat - zkratka ziskat kategorie
        categories = ( '//*[@id="right"]/table[2]/tr[4]/td[2]/ol/li/a/text()' ).extract()

        # TODO: dodelat
        xitems['otherWebsites'] = sel.xpath( '//*[@id="right"]/table[7]/tr[2]/td[1]/ol/li[1]/a/text()' )

        total.update( singles )
        total.update( categories )
        total.update( otherWebsites )

        self.scrapedData = total

class Urlm( Scraper ):
    '''Holder for data from Urlm.com informations'''

    def collect_that_all( self ):
        total = {}




def maternal_that_all( maternalURL ):
    ''' An ultimate function that will return information from all maternal scrapers
    '''

    total = {}

    ### ALEXA ###
    alexa_singles = {
               'link' : '//*[@id="js-li-last"]/span[1]/a',
               'global_rank' : '//*[@id="traffic-rank-content"]/div/span[2]/div[1]/span/span/div/strong',
               'global_rank_change' : '//*[@id="traffic-rank-content"]/div/span[2]/div[2]/span/span/div/strong',
               'in_country' : '//*[@id="traffic-rank-content"]/div/span[2]/div[2]/span/span/h4/a',
               'rank_in_country' : '//*[@id="traffic-rank-content"]/div/span[2]/div[2]/span/span/div/strong',
               'bounce_rate': '//*[@id="engagement-content"]/span[1]/span/span/div/strong',
               'bounce_rate_change' : '//*[@id="engagement-content"]/span[1]/span/span/div/span',
               'daily_pagev_per_vis' : '//*[@id="engagement-content"]/span[2]/span/span/div/strong',
               'daily_pagev_per_vis_change' : '//*[@id="engagement-content"]/span[2]/span/span/div/span',
               'daily_time_on_site' : '//*[@id="engagement-content"]/span[3]/span/span/div/strong',
               'daily_time_on_site_change' : '//*[@id="engagement-content"]/span[3]/span/span/div/span',
               'search_visits' : '//*[@id="keyword-content"]/span[1]/span/span/div/strong',
               'search_visits_change' : '//*[@id="keyword-content"]/span[1]/span/span/div/span',
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

    alexa = Alexa( maternalURL, "www.alexa.com", TODO, alexa_singles, alexa_doubles )
    alexa.collect_that_all()
    total.update( {"alexa" : alexa.scrapedData } )

    ### WebsiteOutlook ###

    # TODO: jeste pridat estimWorth
    webout_singles = {
                    "link" : '//*[@id="right"]/table[1]/tr[1]/td[2]/span/span',
                    "pageviewsPerDay" : '//*[@id="right"]/table[1]/tr[2]/td[2]',
                    "makingUSD" : '//*[@id="right"]/table[1]/tr[3]/td[2]',
                    "websiteoutRank" : '//*[@id="right"]/table[1]/tr[4]/td[2]/span[1]',
                    "backlingsYahoo" : '//*[@id="right"]/table[2]/tr[3]/td[2]',
                    "traficRank" : '//*[@id="right"]/table[2]/tr[1]/td[2]',
                    'pageRank' : '//*[@id="right"]/table[2]/tr[2]/td[2]',
                    }

    websiteout = Websiteout( maternalURL, "www.websiteoutlook", TODO, webout_singles )
    websiteout.collect_that_all()
    total.update( {"websiteout" : websiteout.scrapedData} )


    ### URLM ###
    urlm_singles = {
                    'link' : '/html/body/div[1]/div[2]/div/div[1]/div[1]/span',
                    'global_rank' : '//*[@id="summary"]/div[1]/p[2]/span[1]',
                    'in_country' : '//*[@id="summary"]/div[1]/p[1]/span[2]',
                    'rank_in_country' : '//*[@id="summary"]/div[1]/p[1]/span[1]',
                    'monthly_pages_viewed' : '//*[@id="summary"]/div[2]/table/tbody/tr[1]/td[2]',
                    'monthly_visits' : '//*[@id="summary"]/div[2]/table/tbody/tr[2]/td[2]',
                    'value_per_vis' : '//*[@id="summary"]/div[2]/table/tbody/tr[3]/td[2]',
                    'estimated_worth' : '//*[@id="summary"]/div[2]/table/tbody/tr[4]/td[2]',
                    'external_links' : '//*[@id="summary"]/div[2]/table/tbody/tr[5]/td[2]',
                    'number_of_pages' : '//*[@id="summary"]/div[2]/table/tbody/tr[6]/td[2]',
                    'topics' : '//*[@id="web"]/p[1]',
                    'category' : '//*[@id="web"]/p[2]',
                    'info_per_day' : '//*[@id="web"]/p[3]',
                    }
    urlm = Urlm( maternalURL, "www.urlm.com", TODO, urlm_singles )
    urlm.collect_that_all()
    total.update( {"urlm" : urlm.scrapedData } )

    return( total )
