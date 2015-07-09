from selenium.common.exceptions import NoSuchElementException
from nourisher.utiliser import informer
from time import sleep
ST = 0.5

class Scraper:
    """ This is common interface for all scrapers,
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
    wdriver : selenium.webdriver
        webdriver used for scraping of current instance
    """

    baseURL = ""
    maternalURL = ""
    scrapedData = None
    driver = None

    def __init__(self, _maternalURL, _baseURL, _xpathOfInputField, wdriver):
        """ Init

        Parameters
        ----------
        _maternalURL : string
            URL of maternal website of feed we want to get info about
        baseURL : string
            URL address without http:// of the webpage from which data should be scraped of
        _xpathOfInputField: string
            name of field where is the input field for maternal URL
        wdriver : selenium.webdriver
            driver which should be used for scrapping
        """

        self.driver = wdriver
        self.baseURL = _baseURL
        self.maternalURL = _maternalURL

        self.driver.get(r'http://' + _baseURL + "/" + _maternalURL)
        #inputField = wdriver.find_element_by_xpath(_xpathOfInputField)
        #inputField.clear()
        #inputField.send_keys(_maternalURL)
        #inputField.submit()

        # what happens if no informations are available
        try:
            if self.check_unavailability():
                #wdriver.quit()
                informer("\nNo data from this scrapper.")
                raise RuntimeError("No available data from this Scraper")
        except NoSuchElementException:
            pass

        # TODO: get printscreen of that page and save it


    # def __del__(self):
    #     """If driver haven't been closed, do it now!"""
    #     try:
    #         self.driver.quit()
    #     except:
    #         pass

    def check_unavailability(self):
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

    def fex(self, xpath):
        """Find elements by xpath
        """
        #sleep(ST)
        return self.driver.find_element_by_xpath(xpath)

    def selxs(self, xpath):
        """this is just shorthand for finding text from ALL matching fields

        Parameters
        ----------
        xpath: string
            xpath of wanted elements

        Returns
        -------
        list of strings
            list of texts from scraped values
        """

        try:
            elems = self.driver.find_elements_by_xpath(xpath)
            res = [value.text for value in elems]
        except NoSuchElementException:
            res = None
        #sleep(0.5)
        return res

    def selx(self, xpath):
        """This is just shortage for finding text from ONE matching fields

        Parameters
        ----------
        xpath: string
            xpath of wanted elements

        Returns
        -------
        string
            text from scraped value
        """

        try:
            res = self.fex(xpath).text
        except NoSuchElementException:
            res = None

        return res

    def collect_textual_singles(self, textWantedSingle):
        """Collects all text from items in textWantedSingle

        Parameters
        ----------
        textWantedSingle : dict
            dict in format {nameOfAtt1 : xpath1, nameOfAtt2:xpath2, ...}

        Returns
        -------
        dict
            in format {nameOfAtt1 : value1, nameOfAtt2 : value2,...}
        """

        xitems = {}
        for name, xpath in textWantedSingle.items():
            xitems[name] = self.selx(xpath)

        return xitems

    def collect_textual_singles_lists(self, textWantedSingleList):
        """For attributes in type key: [val1, val2, ...]

        Parameters
        ----------
        textWantedSingleList : dict
            in type {nameOfAtt : xpath}
        
        Returns
        -------
        dict
            in form {nameOfAtt : [val1, val2, ...]}
        """

        xitems = {}
        for key, xpath in textWantedSingleList.items():
            xitems[key] = self.selxs(xpath)

        return xitems

    def _collect_two_zip(self, Axpath, Bxpath):
        """It's common to get data in two collumns (e.g. in tables)

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
        """
        A = self.selxs(Axpath)
        B = self.selxs(Bxpath)

        # used to be a dict, but mongodb can't store things
        # under key which contain a dot
        res = [list(c) for c in zip(A, B)]
        return res

    def collect_textual_doubles(self, textWantedDouble):
        """Collects all text from items in textWantedDouble

        Parameters
        ----------
        textWantedDouble : dict
            in format {attName : (Axpath, Bxpath)}

        Returns
        -------
        dict of dicts
            in format {nameOfCollection : data}, where data is in (nameOfVal, val)
        """

        xitems = {}
        for nameOfCollection, (nameXp, valXp) in textWantedDouble.items():
            xitems[nameOfCollection] = self._collect_two_zip(nameXp, valXp)

        return xitems

    def collect_that_all(self):
        """Collects all possible informations - every instance must implement

        Parameters
        ----------
        maternalURL: url of maternal website of feed

        Returns
        --------
        dict: dictionary with data
        """

        raise NotImplementedError


class Alexa(Scraper):
    """ This holder for Alexa.com informations
    """

    alexa_singles = {
        'link': '//*[@id="js-li-last"]/span[1]/a',
        #'globalRank': '//*[@id="traffic-rank-content"]/div/span[2]/div[1]/span/span/div/strong',
        'rAlexa': '//*[@id="traffic-rank-content"]/div/span[2]/div[1]/span/span/div/strong',
        'globalRankChange': '//*[@id="traffic-rank-content"]/div/span[2]/div[2]/span/span/div/strong',
        'inCountry': '//*[@id="traffic-rank-content"]/div/span[2]/div[2]/span/span/h4/a',
        'rankInCountry': '//*[@id="traffic-rank-content"]/div/span[2]/div[2]/span/span/div/strong',
        'bounceRate': '//*[@id="engagement-content"]/span[1]/span/span/div/strong',
        'bounceRateChange': '//*[@id="engagement-content"]/span[1]/span/span/div/span',
        'dailyPagevPerVis': '//*[@id="engagement-content"]/span[2]/span/span/div/strong',
        'dailyPagevPerVisChange': '//*[@id="engagement-content"]/span[2]/span/span/div/span',
        'dailyTimeOnSite': '//*[@id="engagement-content"]/span[3]/span/span/div/strong',
        'dailyTimeOnSiteChange': '//*[@id="engagement-content"]/span[3]/span/span/div/span',
        'searchVisits': '//*[@id="keyword-content"]/span[1]/span/span/div/strong',
        'searchVisitsChange': '//*[@id="keyword-content"]/span[1]/span/span/div/span',
        'totalSitesLinking': '//*[@id="linksin-panel-content"]/div[1]/span/div/span',
        'relatedLinks': '//*[@id="related_link_table"]/tbody/tr/td/a',
    }

    alexa_doubles = {
        'popKeywords': ('//*[@id="keywords_top_keywords_table"]/tbody/tr/td[1]/span[2]',
                        '//*[@id="keywords_upstream_site_table"]/tbody/tr/td[2]/span'),
        'upstreamSites': ('//*[@id="keywords_upstream_site_table"]/tbody/tr/td[1]/a',
                          '//*[@id="keywords_upstream_site_table"]/tbody/tr/td[2]/span'),
        'whereGoNext': ('//*[@id="subdomain_table"]/tbody/tr/td/span[@class="word-wrap"]',
                        '//*[@id="subdomain_table"]/tbody/tr/td[@class="text-right"]/span')
    }

    def check_unavailability(self):

        status = self.driver.find_element_by_xpath('//*[@id="no-enough-data"]/div/div/span[1]/span/strong').text

        # usually not even here it gets...
        if "We don't have enough data to rank this website." in status:
            return True
        else:
            return False

    def collect_that_all(self):

        total = {}
        singles = self.collect_textual_singles(self.alexa_singles)
        doubles = self.collect_textual_doubles(self.alexa_doubles)

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

        total.update(singles)
        total.update(doubles)
        # total.update( {"categories" : categories} )

        self.scrapedData = total


class Websiteout(Scraper):
    """ This is holder for Websiteoutlook.com informations
    """

    webout_singles = {
        #"link": '//*[@id="right"]/table[1]/tbody/tr[1]/td[2]/span/span',
        "pageviewsPerDay": '//*[@id="basic"]/div[2]/div[2]/table/tbody/tr[7]/td[2]/span',
        "backlingsWebout": '//*[@id="basic"]/div[2]/div[2]/table/tbody/tr[3]/td[2]/span',
        'rAlexa' : '//*[@id="basic"]/div[2]/div[2]/table/tbody/tr[1]/td[2]/span',
        'rGoogle': '//*[@id="basic"]/div[2]/div[2]/table/tbody/tr[2]/td[2]/span',
        'rGooglePlus': '//*[@id="google"]',
        'rFacebook' : '//*[@id="facebook"]',
        'rTwitter' : '//*[@id="twitter"]',
        'rLinkedin' : '//*[@id="linkedin"]',
        'rMozrank' : '//*[@id="basic"]/div[2]/div[2]/table/tbody/tr[6]/td[2]/span',
        'rSemrush' : '//*[@id="sem"]/div[2]/table/tbody/tr[1]/td[2]',
        'rDomainAuthority' : '//*[@id="basic"]/div[2]/div[2]/table/tbody/tr[5]/td[2]/span',
        'rPageAuthority' : '//*[@id="basic"]/div[2]/div[2]/table/tbody/tr[4]/td[2]/span',
        'topKeywords' : '//*[@id="sem"]/div[2]/table/tbody/tr[2]/td[2]',
        'organicTraffic' : '//*[@id="sem"]/div[2]/table/tbody/tr[3]/td[2]',
        'worth' : '//*[@id="basic"]/div[2]/div[2]/table/tbody/tr[8]/td[2]/span',
        'cost' : '//*[@id="sem"]/div[2]/table/tbody/tr[4]/td[2]',
    }

    def check_unavailability(self):

        # pokus o sber
        try:
            status = self.selx('/html/body/div/div[2]/p')
        except NoSuchElementException:
            return False
        if (status is not None) and ("not analyzed please click" in status):
            self.fex('//*[@id="go"]').click()
            try:
                if "No enough Data available" in self.selx('/html/body'):
                    return True
                else:
                    return False
            except NoSuchElementException:
                return False

        if "Not Found" in self.selx('/html/body/h1'):
            self.driver.get('http://' + 'www.' + self.maternalURL)
            try:
                if self.notfound_counter:
                    return True
            except AttributeError:
                self.notfound_counter = True
                self.check_unavailability()

        return False

    def collect_that_all(self):

        try:
            self.fex('//*[@id="basic"]/div[2]/div[2]/table/tbody/tr[9]/td/form/button').click()
        except NoSuchElementException:
            pass

        total = {}
        singles = self.collect_textual_singles(self.webout_singles)

        categories = self.selxs('//*[@id="right"]/table[2]/tbody/tr[4]/td[2]/ol/li/a')

        otherSites = self.selxs('//*[@id="right"]/table[7]/tbody/tr[2]/td[1]/ol/li/a')

        txtpg = {'textRatio' : (self.selx('//*[@id="website"]/div[2]/dl/dd[17]'), r"%") ,
                 'pageSize' : (self.selx('//*[@id="website"]/div[2]/dl/dd[16]'), "Kb")
                }

        for tag, (txt, sp) in txtpg.items():
            try:
                a = txt.split(sp)[0]
                txtpg[tag] = a
            except AttributeError:
                pass

        total.update(txtpg)

        total.update(singles)
        total.update({'categories': categories})
        total.update({'otherSites': otherSites})

        self.scrapedData = total


class Urlm(Scraper):
    """Holder for data from Urlm.com informations"""

    # TODO: Needs a lot of polishin - specially age, category, sitesLinkingIn/Out, popPages

    urlm_singles = {
        'link': '/html/body/div[1]/div[2]/div/div[1]/div[1]/span',
        'globalRank': '//*[@id="summary"]/div[1]/p[2]/span[1]',
        'inCountry': '//*[@id="summary"]/div[1]/p[1]/span[2]',
        'rankInCountry': '//*[@id="summary"]/div[1]/p[1]/span[1]',
        'monthlyPagesViewed': '//*[@id="summary"]/div[2]/table/tbody/tr[1]/td[2]',
        'monthlyVisits': '//*[@id="summary"]/div[2]/table/tbody/tr[2]/td[2]',
        'valuePerVis': '//*[@id="summary"]/div[2]/table/tbody/tr[3]/td[2]',
        'estimatedWorth': '//*[@id="summary"]/div[2]/table/tbody/tr[4]/td[2]',
        'externalLinks': '//*[@id="summary"]/div[2]/table/tbody/tr[5]/td[2]',
        'numberOfPages': '//*[@id="summary"]/div[2]/table/tbody/tr[6]/td[2]',
        'topics': '//*[@id="web"]/p[1]',
        'category': '//*[@id="web"]/p[2]',
        'infoPerDay': '//*[@id="web"]/p[3]',
    }
    urlm_singles_lists = {'sitesLinkingIn': '//*[@id="web"]/ul[2]/li',
                          'sitesLinkingOut': '//*[@id="web"]/ul[3]/li',
                          'popPages': '//*[@id="web"]/ul[1]/li',
                          }

    urlm_doubles = {'rankPerCountries': ('//*[@id="summary"]/div[5]/table/tr/td[1]',
                                         '//*[@id="summary"]/div[5]/table/tr/td[2]'),
                    'average90Days': ('//*[@id="visitors"]/table[3]/tr/th',
                                      '//*[@id="visitors"]/table[3]/tr/td[2]'),
                    }

    def check_unavailability(self):

        status = self.driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/div/div/div/h3').text

        if "Sorry, we do not have data on this website" in status:
            return True
        else:
            return False

    def collect_that_all(self):
        total = {}

        singles = self.collect_textual_singles(self.urlm_singles)
        _singlesLists = self.collect_textual_singles_lists(self.urlm_singles_lists)

        # take out first rubish
        singlesLists = {}
        for key, listik in _singlesLists.items():
            singlesLists[key] = listik[1:]

        doubles = self.collect_textual_doubles(self.urlm_doubles)

        total.update(singles)
        total.update(singlesLists)
        total.update(doubles)

        self.scrapedData = total


### RANKS ###

class RankerDist(Scraper):
    """Holder for ranks"""

    _rankNames = [#'rGoogle',
                  'rCompete',
                  #'rMozrank',
                  'rSeznam',
                  'rBacklinksG',
                  'rMajestic',
                  'rSiteExplorer',
                  #'rFacebook',
                  #'rTwitter',
                   #'rPlusoneG'
                  ]

    @staticmethod
    def to_digit(lex_numb):
        """Prevede rank na cislo, je-li to mozne"""
        from locale import atof

        try:
            if lex_numb == None:
                numb = None
            elif lex_numb == "N/A":
                numb = None
            elif "/" in lex_numb:
                val = lex_numb.split("/")[0]
                if "-" in val:
                    numb = None
                else:
                    numb = atof(val)
            # for google backlinks
            elif ";" in lex_numb:
                numb = lex_numb
            else:
                numb = atof(lex_numb)
        except ValueError:
            # print( "Chyba prevodu: ", lex_numb, ". Vracim stejny string." )
            numb = lex_numb
        return numb

    def check_unavailability(self):
        # workarround
        try:
            if "is not ranked by" in self.selx('//*[@id="l"]/div[3]/p[3]'):
                return True
        except (NoSuchElementException, TypeError):
            return False

    def get_twitter(self):
        import requests

        r = requests.get("http://urls.api.twitter.com/1/urls/count.json?url={}".format(self.maternalURL))
        return {"rTwitter":eval(r.content.decode("utf8"))["count"]}

    def get_fb_total(self):
        import requests

        r = requests.get("https://api.facebook.com/method/links.getStats?urls={}&format=json".format(self.maternalURL))
        return {"rFacebook" : eval(r.content.decode("utf8"))[0]["total_count"]}

    def get_seznam(self):
        self.driver.get(self.maternalURL)
        res = {
        #"rGoogle" : self.selx('//*[@id="val1"]'),
        "rSeznam" : self.selx('//*[@id="val2"]'),
        }
        return res

    def get_mozrank(self):
        self.driver.get('https://moz.com/researchtools/ose/comparisons?site={}'.format(self.maternalURL))
        res = {"rMozrank" : self.selx('//*[@id="main"]/div/section[2]/div/section[2]/div/div[1]/div/div[2]/table/tbody/tr[2]/td[2]'),
               "rSiteExplorer" : self.selx('//*[@id="main"]/div/section[2]/div/section[2]/div/div[1]/div/div[2]/table/tbody/tr[5]/td[2]')}
        return res

    def get_compete(self):
        sleep(1)
        self.driver.get('http://moonsy.com/compete-rank/')
        self.fex('//*[@id="domain"]').clear()
        self.fex('//*[@id="domain"]').send_keys(self.maternalURL)
        self.fex('//*[@id="form1"]/input[3]').click()
        return {"rCompete": self.selx('//*[@id="l"]/div[3]/p[4]/strong')}

    def login_majestic(self):
        #self.driver.get('https://majestic.com/account/login')
        self.fex('//*[@id="emailPlaceholder1"]').click()
        from time import sleep
        sleep(0.5)
        self.fex('//*[@id="email1"]').send_keys('kotrfa@gmail.com')
        self.fex('//*[@id="passwordPlaceholder1"]').click()
        sleep(0.5)
        self.fex('//*[@id="password1"]').send_keys('seznam12')
        #chkb = self.fex('//*[@id="RememberMe"]')
        #if not chkb.is_selected():
            #sleep(0.5)
            #chkb.click()
        sleep(0.5)
        self.fex('//*[@id="password1"]').submit()


    def get_majestic(self):
        self.driver.get('https://majestic.com/reports/site-explorer?q={}'.format(self.maternalURL))
        try:
            if "Quickly! Register for a FREE account now to continue." in self.selx('//*[@id="usage_blocked"]/div[1]/h3'):
                self.login_majestic()
                #self.driver.get('https://majestic.com/reports/site-explorer?q={}'.format(self.maternalURL))
        except NoSuchElementException:
            pass

        return {"rMajestic" : self.selx('//*[@id="summary_container"]/div[2]/table[1]/tbody/tr[1]/td[1]/div/p[2]/b')}

    def get_gbacklinks(self):
        self.driver.get('https://checker.monitorbacklinks.com/seo-tools/free-backlink-checker/')
        self.fex('//*[@id="checkbacklinksform"]/fieldset[1]/div/p/input').send_keys(self.maternalURL)
        self.fex('//*[@id="checkbacklinksform"]/fieldset[1]/p/button').click()

        return {"rBacklingsG": self.selx('/html/body/div[3]/ul/li[1]/p')}


    def collect_that_all(self):
        d = {}
        # not needed thanks to websiteout: [self.get_fb_total(),self.get_mozrank(), self.get_twitter(), self.get_seznam()]
        _ranks = [self.get_compete()]
                  #self.get_gbacklinks(),
                  #self.get_majestic()]

        for dic in _ranks:
            d.update(dic)

        ranks = dict([(rankname, self.to_digit(lexNumb)) for rankname, lexNumb in d.items()])

        self.scrapedData = ranks


# class RankerJklir(Scraper):
#     """Holder for ranks"""
#
#     _rankNames = ['rGoogle',
#                   'rAlexa',
#                   'rCompete',
#                   'rMozrank',
#                   'rSeznam',
#                   'rBacklinksG',
#                   'rMajestic',
#                   'rSiteExplorer',
#                   'rFacebook',
#                   'rTwitter',
#                   #'rPlusoneG'
#                   ]
#
#     @staticmethod
#     def to_digit(lex_numb):
#         """Prevede rank na cislo, je-li to mozne"""
#         from locale import atof
#
#         try:
#             if lex_numb == "N/A":
#                 numb = None
#             elif "/" in lex_numb:
#                 val = lex_numb.split("/")[0]
#                 if "-" in val:
#                     numb = None
#                 else:
#                     numb = atof(val)
#             # for google backlinks
#             elif ";" in lex_numb:
#                 numb = lex_numb
#             else:
#                 numb = atof(lex_numb)
#         except ValueError:
#             # print( "Chyba prevodu: ", lex_numb, ". Vracim stejny string." )
#             numb = lex_numb
#         return numb
#
#     def check_unavailability(self, wdriver):
#
#         try:
#             wfex('//*[@id="content"]/center/table[1]/tbody/tr/td[1]/a/img')
#             return False
#         except NoSuchElementException:
#             raise RuntimeError("Problem! Pravdepodobne jsem dostal ban!")
#
#     def collect_that_all(self):
#         _ranks = self.selxs('//*[@id="content"]/center/table/tbody/tr/td[2]')
#         ranks = [self.to_digit(lexNumb) for lexNumb in _ranks]
#
#         self.scrapedData = dict(zip(self._rankNames, ranks))


def maternal_that_all(maternalURL, webdriver, deal=None):
    """ An ultimate function for module that will return
     information from all scrapers.

    Parameters
    ----------
    maternalURL : string
        URL for which we want to get informations
    deal : list of strings (names of scrapers)
        name of scrapers in list from which we want to scrap data

    Returns
    -------
    dict
        dictionary that holdes all collected informations
    """
    if not deal:
        deal = ["websiteout", "urlm", "ranks", "alexa"]
    # every scraper must be named here in format:
    # {"nameOfScraper" : (ClassOfScrapper, baseURL, xPathOfInputField)}
    available_scrapers = {"websiteout": (Websiteout, "www.websiteoutlook.com", '//*[@id="analyse"]/div/input'),
                          "urlm": (Urlm, "www.urlm.co", '//*[@id="url"]'),
                          "ranks": (RankerDist, "www.google.com", '//*[@id="lst-ib"]'),
                          "alexa": (Alexa, "www.alexa.com/siteinfo", '//*[@id="search-bar"]/form/input')
                          }

    rouse = dict([(dom, inf) for dom, inf in available_scrapers.items() if dom in deal])
    total = {}
    for name, (cls, baseURL, xpathOfInput) in rouse.items():
        informer("Trying to get data for {0} by {1}".format(maternalURL, name), rewrite=True)
        try:
            curcl = cls(maternalURL, baseURL, xpathOfInput, webdriver)
            curcl.collect_that_all()
            total.update({name: curcl.scrapedData})
            informer("\nSucceded.", rewrite=True)
            #sleep(ST)
        except RuntimeError:
            informer("\nNot successful.")
            total.update({name: None})

    return total
