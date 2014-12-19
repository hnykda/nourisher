'''
Created on Dec 19, 2014

@author: dan
'''
import unittest

class Test(unittest.TestCase):
    '''Testing suite for collector
    
    Atributes
    ---------
    testingUrl: For future this should be something static...
    
    '''
    
    testingUrl = 'http://www.huffingtonpost.com/news/authors/feed/'

    def testName(self):
        pass
        
    
    


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()