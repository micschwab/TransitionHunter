import glob
import os
import json
import shutil
import astropy
import tabulate
import numpy as np
import pandas as pd
from io import StringIO
from astropy.io import fits
from specutils import Spectrum1D
from wiserep_api import download_target_spectra
"""

This Module handle the reading/organization of spectra by either/or both methods:

    (1) Quering WiseRep using WiseRep_api to download ascii and/or fits files
    
    (2) Searching for spectra in the provided /spectra directory 
    
Spectra once downloaded will be organized in a /spectra if one does not already exist


Developer Notes:
By default, WiseRep_API will download fits & ascii files (choosing one excludes the other --> possible to miss spectra)
"""

#test with 3 different SNe

def get_WISeREP_spectra(sn):
    """

    This function calls the WiseRep_api function: download_target_spectra()
    (Wiserep_API: https://github.com/temuller/wiserep_api)

    For a given SN name (i.e 2025vzq), spectra will be downloaded (as .fits and/or .ascii)
    into a /spectra/SNname/ subfolder structure in the working directory along with a csv file 
    containing spectrum information such as IAU name, Date of Observation etc.
    ---------------------------------------------------------------------
    Parameters:
        - sn (string): the SN name i.e. '2025vzq'

    Returns: None

    """
    print(f'Downloading SN {sn} spectra from WISeREP...')

    download_target_spectra(sn) 

    #read and print ouput of download 
    download_info = pd.read_csv(f'spectra/{sn}/downloaded_spectra_info.csv')

    relevant_columns = {
        'IAU Name': download_info['Obj. IAU Name'],
        'Obj type': download_info['Obj Type'],
        'Redshift': download_info['Redshift'],
        'Obs-date (UT)': download_info['Obs-date (UT)'],
        'Tel / Inst': download_info['Tel / Inst'],
        'Spectrum ascii File': download_info['Spectrum ascii File'],
        'Spectrum fits File': download_info['Spectrum fits File']
    }

    output_info = pd.DataFrame(relevant_columns)
    print(output_info.to_markdown(index=False))

    return None


def organize_imports(sn, searchWiseRep):
    """  

    This function organizes all spectra into /spectra and 
    removes duplicates preferring fits files
    
    All data/information provided/downloaded is copied and stored 
    for posterity into a folder in the working direcroty: /raw
    ---------------------------------------------------------------------
    Parameters:
        - sn (string): the SN name i.e. '2025vzq'
        - searchWiseRep (boolean): if True this function will 'unpack' the WiseRep Download

    Returns: None

    """

    print('organizing files...')
    
    #### UNPACK WISeREP DOWNLOAD ################
    
    #check if WiseRep Download occured
    if searchWiseRep:

        # Move WiseReP imports out of object specific subfolder (TransitionmHunter runs on one object at a time)
        ##  ~ could be changed in future iterations to run TransitionHunter on multiple objects at a time ~
        for filename in os.listdir(f'./spectra/{sn}'):
            source_path = os.path.join(f'./spectra/{sn}', filename)
            destination_path = os.path.join('./spectra', filename)

            shutil.move(source_path, destination_path)

        #remove now-empty subfolder
        os.rmdir(f'./spectra/{sn}')

    #create a folder for the downloaded/provided spectra as given 
    shutil.copytree(f'./spectra', './raw')

    #Remove WiseRep CSV from ./spectra folder
    if os.path.exists('./spectra/'):
        os.remove('./spectra/downloaded_spectra_info.csv')

    ###############################################

    #### ClEAN WORKING DIRECTORY ################

    #check for duplicates in the ./spectra directory
    dat_extensions = ['.txt', '.ascii', '.dat']
    fits_ext = '.fits'

    path = f'./spectra/*'
    files = [os.path.basename(f) for f in glob.glob(path)]

    #split filename from ext
    base_names = np.array([])
    exts = np.array([])

    #read in files
    for file in files:
        name, ext = os.path.splitext(file)
        base_names = np.append(base_names,name)
        exts = np.append(exts, ext)

    #INSERT CODE HERE TO REMOVE DUPLICATES ONCE TESTED IN TESTIMPORTS
            
    
    pass