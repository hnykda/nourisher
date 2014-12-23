from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from nourisher.settings import DEFAULT_DRIVER
from nourisher.utiliser import informer

class Scraper:
    ''' This is common interface for all scrapers, 
    like these for Alexa.com, urlm.com, websiteoutlook.com, etc.
    
    This class should not be called directly - there should be descendants implemented
    who inherits from this class.
    
    Note
    -----
    There should not be any wrangling - save it as it is somewhere and
    after that wrangling can come - there might be errors during it and
    it is inconvenient to collect data again if they are corrupted.
    
    **Adding new scrapper** To add a new scrapper is necessary to:
    
    1. Create descendant of Scraper - find out scrapper baseURL, 
    xpath of input field, xpaths for data to scrap, implement necessary
    functions (e.g. `check_unavailability()`, `collect_all()` ) 
    2. Add entry to maternal_that_all()
    3. Implement methods for cleaning data
        
    Atributes
    ---------
    baseURL : string 
        URL address without http:// of the webpage from which data should be scraped of
    maternalURL : string 
        URL of maternal website of feed we want to get info about
    scrapedData : dict
        Data scraped from the website
    driver : selenium.webdriver
        webdriver used for scraping of current instance
    '''

    baseURL = ""
    maternalURL = ""
    scrapedData = None
    driver = None


    def __init__( self, _maternalURL, _baseURL, _xpathOfInputField, browser = DEFAULT_DRIVER ):
        ''' Init
        
        Parameters
        ----------
        _maternalURL : string
            URL of maternal website of feed we want to get info about
        baseURL : string 
            URL address without http:// of the webpage from which data should be scraped of
        _xpathOfInputField: string 
            name of field where is the input field for maternal URL
        browser: string, optinal
            
            Defaults to nourisher.settings.DEFAULT_DRIVER
            
            One of ["firefox", "firefoxTOR", "phatnomjs", "phantomjsTOR"]
            
            Specify which browser you want to use for scrapping and if you want 
            to use TOR version or not (TOR must be running at localhost:9050, socks5!) 
        '''

        self.baseURL = _baseURL

        if browser == "phantomjs":
            wdriver = webdriver.PhantomJS()
        elif browser == "phantomjsTOR":
            serviceArgs = ['--proxy=localhost:9050', '--proxy-type=socks5']
            wdriver = webdriver.PhantomJS( service_args = serviceArgs )
        elif browser == "firefox":
            wdriver = webdriver.Firefox()
        elif browser == "firefoxTOR":
            profile = webdriver.FirefoxProfile()
            profile.set_preference( 'network.proxy.type', 1 )
            profile.set_preference( 'network.proxy.socks', 'localhost' )
            profile.set_preference( 'network.proxy.socks_port', 9050 )
            wdriver = webdriver.Firefox( profile )

        wdriver.get( r'http://' + _baseURL )
        inputField = wdriver.find_element_by_xpath( _xpathOfInputField )
        inputField.clear()
        inputField.send_keys( _maternalURL )
        inputField.submit()

        # what happens if no informations are available
        try:
            if self.check_unavailability( wdriver ) == True:
                wdriver.close()
                informer( "\nNo data from this scrapper." )
                raise RuntimeError ( "No available data from this Scraper" )
        except NoSuchElementException:
            pass

        # TODO: get printscreen of that page and save it

        self.driver = wdriver

    def check_unavailability( self, wdriver ):
        """Checks if information of scrapper are available
        
        Note
        -----
        
        All descendants must implement this function
        
        Parameters
        ----------
        wdriver : selenium.webdriver instance
            current webdriver 
        
        Returns
        -------
        bool
            True if no informations are provided, else False (and hence, continue)
        """

        # children must implement
        raise NotImplementedError

    def selxs( self, xpath ):
        '''this is just shorthand for finding text from ALL matching fields
        
        Parameters
        ----------
        xpath: string
            xpath of wanted elements
            
        Returns
        -------
        list of strings
            list of texts from scraped values
        '''

        try:
            elems = self.driver.find_elements_by_xpath( xpath )
            res = [value.text for value in elems]
        except NoSuchElementException:
            res = None

        return( res )

    def selx( self, xpath ):
        '''This is just shortage for finding text from ONE matching fields
        
        Parameters
        ----------
        xpath: string
            xpath of wanted elements
            
        Returns
        -------
        string
            text from scraped value
        '''

        try:
            res = self.driver.find_element_by_xpath( xpath ).text
        except NoSuchElementException:
            res = None

        return( res )

    def collect_textual_singles( self, textWantedSingle ):
        '''Collects all text from items in textWantedSingle
        
        Parameters
        ----------
        textWantedSingle : dict
            dict in format {nameOfAtt1 : xpath1, nameOfAtt2:xpath2, ...}
        
        Returns
        -------
        dict
            in format {nameOfAtt1 : value1, nameOfAtt2 : value2,...}
        '''

        xitems = {}
        for name, xpath in textWantedSingle.items():
            xitems[name] = self.selx( xpath )


        return( xitems )

    def collect_textual_singles_lists( self, textWantedSingleList ):
        '''For attributes in type key: [val1, val2, ...]
        
        Parameters
        ----------
        textWantedSingleList : dict
            in type {nameOfAtt : xpath}
        
        Returns
        -------
        dict
            in form {nameOfAtt : [val1, val2, ...]}
        '''

        xitems = {}
        for key, xpath in textWantedSingleList.items():
            xitems[key] = self.selxs( xpath )

        return( xitems )

    def _collect_two_zip( self, Axpath, Bxpath ):
        '''It's common to get data in two collumns (e.g. in tables)
        
        Parameters
        ----------
        Axpath : list of strings (xpaths)
            xpaths of first column (usually names for values in Bxpath)
        Bxpath : list of strings (xpaths)
            xpaths of second column (usually values for keys in Axpath)
        
        Returns
        -------
        list of tuples
            in format {AxpathValue1 : BxpathValue1, ,...}
        
        Note
        -----
        Returns list of tuples instead of dict, because mongodb can't store 
        under names with "." (dot) in them. This was problem when storing 
        e.g. {"google.com" : "13.4%"}.
        '''
        A = self.selxs( Axpath )
        B = self.selxs( Bxpath )

        # used to be a dict, but mongodb can't store things
        # under key which contain a dot
        res = [list( c ) for c in zip( A, B )]
        return( res )

    def collect_textual_doubles( self, textWantedDouble ):
        '''Collects all text from items in textWantedDouble
        
        Parameters
        ----------
        textWantedDouble : dict
            in format {attName : (Axpath, Bxpath)}
        
        Returns
        -------
        dict of dicts 
            in format {nameOfCollection : data}, where data is in (nameOfVal, val) 
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
        dict: dictionary with data
        '''

        raise NotImplementedError

    def close_driver( self ):
        self.driver.close()

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

    def check_unavailability( self, driver ):

        status = driver.find_element_by_xpath( '//*[@id="no-enough-data"]/div/div/span[1]/span/strong' ).text

        # usually not even here it gets...
        if "We don't have enough data to rank this website." in status:
            return( True )
        else:
            return( False )


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

    def check_unavailability( self, driver ):

        status = driver.find_element_by_xpath( '/html/body' ).text

        if "Not a Valid Domain#2" in status or "no data" in status:
            return( True )
        else:
            return( False )


    def collect_that_all( self ):
        total = {}
        singles = self.collect_textual_singles( self.webout_singles )

        categories = self.selxs( '//*[@id="right"]/table[2]/tbody/tr[4]/td[2]/ol/li/a' )

        otherSites = self.selxs( '//*[@id="right"]/table[7]/tbody/tr[2]/td[1]/ol/li/a' )

        # estimated worth
        try:
            text = self.selxs( '//*[@id="right"]/div[3]/p' )
            splText = text[0].split()
            splText.reverse()
            iDofWorth = splText.index( "USD" )
            worth = splText[iDofWorth - 1]
            potVal = splText[iDofWorth - 2]
            if potVal in ["Million", "Billion"]:
                worth += " " + potVal
        except ValueError:
            worth = None
        total.update( {'estimatedWorth' :  worth} )

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

    def check_unavailability( self, driver ):

        status = driver.find_element_by_xpath( '/html/body/div/div[2]/div/div/div/div/h3' ).text

        if "Sorry, we do not have data on this website" in status:
            return( True )
        else:
            return( False )

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

    _rankNames = ['rGoogle',
         'rAlexa',
         'rCompete',
         'rMozrank',
         'rSeznam',
         'rJyxo',
         'rBacklinksG',
         'rMajestic',
         'rSiteExplorer',
         'rFacebook',
         'rTwitter',
         'rPlusoneG'
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

    def check_unavailability( self, wdriver ):

        try:
            wdriver.find_element_by_xpath( '//*[@id="content"]/center/table[1]/tbody/tr/td[1]/a/img' )
            return( False )
        except NoSuchElementException:
            raise RuntimeError ( "Problem! Pravdepodobne jsem dostal ban!" )

    def collect_that_all( self ):
        _ranks = self.selxs( '//*[@id="content"]/center/table/tbody/tr/td[2]' )
        ranks = [self.to_digit( lexNumb ) for lexNumb in _ranks]

        self.scrapedData = dict( zip( self._rankNames, ranks ) )

def collect_alexa( maternalURL ):
    alexa = Alexa( maternalURL, "www.alexa.com", '//*[@id="alx-content"]/div/div/span/form/input' )
    alexa.collect_that_all()
    alexa.close_driver()
    return( alexa.scrapedData )

def collect_websiteout( maternalURL ):
    websiteout = Websiteout( maternalURL, "www.websiteoutlook.com", '//*[@id="header"]/form/input[1]' )
    websiteout.collect_that_all()
    websiteout.close_driver()
    return ( websiteout.scrapedData )

def collect_urlm( maternalURL ):
    urlm = Urlm( maternalURL, "www.urlm.co", '//*[@id="url"]' )
    urlm.collect_that_all()
    urlm.close_driver()
    return( urlm.scrapedData )

def collect_ranks( maternalURL ):
    ranks = Ranker( maternalURL, "pagerank.jklir.net", '//*[@id="url"]' )
    ranks.collect_that_all()
    ranks.close_driver()
    return( ranks.scrapedData )

def maternal_that_all( maternalURL ):
    ''' An ultimate function for module that will return
     information from all scrapers.
     
    Parameters
    ----------
    maternalURL : string
        URL for which we want to get informations
    
    Returns
    -------
    dict
        dictionary that holdes all collected informations
    
    
    
    TODO: This could even replace functions above
    '''

#     classes = [Websiteout, Urlm, Ranker, Alexa]
#     correspInit = [
#                     ( "www.websiteoutlook.com", '//*[@id="header"]/form/input[1]' ),
#                     ( "www.urlm.co", '//*[@id="url"]' ),
#                     ( "pagerank.jklir.net", '//*[@id="url"]' ),
#                     ( "www.alexa.com", '//*[@id="alx-content"]/div/div/span/form/input' ),
#                     ]
#     correspNames = ["websiteout", "urlm", "ranks", "alexa"]

    # every scraper must be named here in format:
    # {"nameOfScraper" : (ClassOfScrapper, baseURL, xPathOfInputField)}
    rouse = {"websiteout" : ( Websiteout, "www.websiteoutlook.com", '//*[@id="header"]/form/input[1]' ),
             "urlm": ( Urlm, "www.urlm.co", '//*[@id="url"]' ),
             "ranks" : ( Ranker, "pagerank.jklir.net", '//*[@id="url"]' ),
             "alexa" : ( Alexa, "www.alexa.com", '//*[@id="alx-content"]/div/div/span/form/input' )
             }

    total = {}
    for name, ( cls, baseURL, xpathOfInput ) in rouse.items():
        informer( "Trying to get data for {0} by {1}".format( maternalURL, name ), rewrite = True )
        try:
            curcl = cls( maternalURL, baseURL, xpathOfInput )
            curcl.collect_that_all()
            curcl.close_driver()
            total.update( {name : curcl.scrapedData } )
            informer( "Succeded.", rewrite = True )
        except RuntimeError:
            informer( "Not successful." )
            total.update( {name : None} )

    return( total )

#     total = {}
#     for dom, func in zip( ["websiteout", "urlm", "alexa", "ranks"],
#                          [collect_websiteout, collect_urlm, collect_alexa, collect_ranks] ):
#         informer( "Trying to get data for {0} by {1}".format( maternalURL, dom ), rewrite = True )
#         try:
#             total.update( {dom : func( maternalURL ) } )
#             informer( "Succeded.", rewrite = True )
#         except RuntimeError:
#             informer( "Not successful." )
#             total.update( {dom : None} )
#
#
#     return( total )
