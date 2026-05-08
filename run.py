import sys
import os
import glob
import pandas as pd
from io import StringIO
import spectra
import runSNIDsage
import transition

"""
This module runs TransitionHunter

All output is saved to "transition.log"

SNID-SAGE summary and diagnostic plots saved in snid_results/ 
--------------------------------------------------------------
Functions:
 - run_TransitionHunter(): wrapper for all tools/logic

Classes: 
- Tee(): manages output so it is written and printed simultaneusly
"""

class Tee(object):
    """
    This class will mimic Unix "tee" command and allow
    data written to the log to be redirected simultaneusly to standard output.
    
    Methods:
     - write(obj): writes string representation of an object to all streams
     - flush(): ensures live-stream/real-time output
    """
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush() # Ensures real-time updates
    def flush(self):
        for f in self.files:
            f.flush()
            
def run_TransitionHunter(sn, searchWiseRep=False, z=None):
    """
    This function wraps all operations/analysis of the program

    Parameters:
    ---------------------------------------------
    sn (string): object name 
    
    searchWiseRep (boolean): Flags wheter or not to query WISeREP for SN spectra,  
                             False by default
                             
    showPlots (boolean): Flags whether or not to show plots, True by Default

    z (float): Option to set redshift if known for your object (improves spectral identification)

    Returns: None
    
    """
    
    ############## Open the log file #######################
    
    original_stdout = sys.stdout #store original output to restore later
    log_file = open('transition.log', 'w')

    #redirect to log file and terminal
    sys.stdout = Tee(original_stdout, log_file)
    
    try:
        # #redirect all standard output to that file
        # sys.stdout = log_file
    
    
        ################### Query WISeREP #######################
        # Optional: Download spectra if searchWiseRep == True
        # # Save downloads to spectra/ directory
        
        if searchWiseRep == True:
            spectra.get_WISeREP_spectra(sn)
    
            
        ################### ORGANIZE FILES #######################
        # Copy files into a raw/ directory and remove duplicate spectra
        # and download information from the working directory: spectra/
        
        spectra.organize_imports(sn, searchWiseRep)
    
        
        ################### RUN SNID-SAGE #######################
        # Run SNID-SAGE and print the live output
        # Store results in snid_results/ directory
        
        print("RUNNING SNID-SAGE...")
        print("#"* 100)
        
        runSNIDsage.run_SNID_SAGE_batch('spectra/*', z)
    
        
        ##################### READ OUTPUT #######################
        # get a dataframe of relevant information from successful 
        # SNID-SAGE analyses sorted chronologically by date of observation
        
        success_df = runSNIDsage.analyze_output('snid_results/')
        
        print("SNID-Sage Analysis completed. For detailed output check snid_results/ folder.\n")
        
            
        ######### SEARCH FOR EVIDENCE OF A TRANSITION ###########
        print("Searching for evidence of a transition...")
        print("#" * 100)
    
        has_transitioned = transition.hunt(sn, success_df)
    
    finally:
        ########################################################
        # # #Close log (very end of script)
        sys.stdout = original_stdout #restore original output
        log_file.close() #close file
    
    return None