'''
Created on Dec 20, 2014

@author: dan
'''
import unittest
from nourisher import utiliser

class Test( unittest.TestCase ):


    def test_mean_var_z_listu( self ):

        vyslT = utiliser.mean_a_var_z_listu( [2, 4, 8, 12, 123] )
        vyslN = utiliser.mean_a_var_z_listu( [3] )

        self.assertAlmostEqual( vyslT, ( 29.8, 46.726437912599323 ), 5 )
        self.assertEqual( ( 3.0, 0.0 ), vyslN )
        self.assertRaises( TypeError, utiliser.mean_a_var_z_listu, None )

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
