import os
import sys
import glob
import tabulate
import pandas as pd
from io import StringIO
from astropy.io import fits
import numpy as np
import astropy
from wiserep_api import download_target_spectra
import searchWiseRep

"""
Runs TransitionHunter

Output printed and saved to a 'TransitionHunter.log'

"""


# Open the log file
log_file = open('TransitionHunter.log', 'w')

#redirect all standard output to that file
sys.stdout = log_file

########################################################


def run(sn, searchWiseRep=False, showPlots=True, z=None):
    """
    This function wraps all operations/analysis of the program

    Parameters:
    ---------------------------------------------
    sn (string): object name 
    
    searchWiseRep (boolean): Flags wheter or not to query WISeREP for SN spectra,  
                             False by default
                             
    showPlots (boolean): Flags whether or not to show plots, True by Default

    z (float): Option to set redshift if known for your object (improves spectral identification)
    
    """
    
#download spectra if searchWiseRep == True

if searchWiseRep:
    spectra.get_WISeREP_spectra(sn)
    
#organize spectra

#run SNID

#analyze output

#printresults

########################################################
#Close log (very end of script)
log_file.close()
