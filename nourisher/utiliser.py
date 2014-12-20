'''
Created on Dec 20, 2014

@author: dan

Here are some utilities that might be useful
'''

def mean_a_var_z_listu( lentry ):
    """Returns mean and std from list of numbers
    
    Parameters
    -----------
    Array of numbers
    
    Returns
    -------
    (mean, std)
    """
    import numpy as np

    return ( np.mean( lentry ), np.std( lentry ) )
