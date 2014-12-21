import pandas as pd
from selenium import webdriver
from ..utiliser import wrangle_numbers

class Scraper:
    ''' This is common interface for all scrapers, 
    like these for Alexa.com, urlm.com, websiteoutlook.com, etc.
    
    There should not be any wrangling - save it as it is somewhere and
    after that wrangling can come - there might be errors during it and
    it is inconvenient to collect data again if they are corrupted.
        
    Atributes
    ---------
    baseURL: URL address of the webpage from which data should
    be scraped of
    maternalURL: URL of maternal website of feed we want to get info about
    textWanted: Dict in format {nameOfAttribut : xpathOfAttribut} 
    to all items that should be scraped for the text inside them
    scrapedData: All data which were scraped
    
    Note
    ----
    TODO: xpaths could be probably be replaced by better selector
    methods, since selenium is capable of many different approaches  
        
    '''

    baseURL = ""
    maternalURL = ""
    textWanted = {}
    scrapedData = None
    nameOfInputField = ""
    # this is selenium phantomJS scraper 
    driver = None
    

    def __init__(self, _baseURL, _maternalURL, _nameOfInputField):
        self.baseURL =  _baseURL
        
        wdriver = webdriver.PhantomJS()
        wdriver.get(_baseURL)
        inputField = wdriver.find_element_by_name("_nameOfInputField")
        inputField.send_keys(_maternalURL)
        wdriver.submit()
        
        # TODO: get printscreen of that page and save it
        
        self.driver = wdriver

    def selxs(self, xpath):
        '''this is just shortage for finding ALL matching fields'''
        return(self.driver.select_elements_by_xpath(xpath))
    
    def selx(self, xpath):
        '''this is just shortage for finding ONE matching fields'''
        return(self.driver.select_element_by_xpath(xpath))
    
    def zip_two(self, Axpath, Bxpath):
        '''It's common to get data in two collumns (e.g. in tables)
        so this will return them in pandas serie
        ''̈́'

    def collect_textual( self ):
        '''Collects all text from items in textWanted
        
        Returns
        -------
        pandas serie wrangled to numbers and time from strings
        '''

        xitems = {}
        for name, xpath in self.textWanted:
            xitems[name] = self.selx(xpath).text
        
             
        return( pd.Series( xitems ) )

    def matern_that_all( self, maternalURL ):
        '''Collects all possible informations - every instance must implement
         
        Parameters
        ----------
        maternalURL: url of maternal website of feed
        
        Returns
        --------
        pandas-serie with data
        '''

        raise Exception

    def 
