import os
import sys
import glob
import tabulate
import pandas as pd
from io import StringIO
import spectra
import runSNIDsage
import transition
import plotResults

"""
Runs TransitionHunter

Output printed and saved to 'transition.log'
Diagnostic plots saved in results/ 

"""

def run_TransitionHunter(sn, searchWiseRep=False, showPlots=True, z=None):
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
    
    log_file = open('transition.log', 'w')
    
    #redirect all standard output to that file
    sys.stdout = log_file


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

    
    ################### GENERATE PLOTS  #####################
    # Plot Confident Class IDs if a transition has occured
    # if has_transitioned == True:
    #     plotResults.make_plots(legit_classes, showPlots)

    ########################################################
    #Close log (very end of script)
    log_file.close()
    
    return None