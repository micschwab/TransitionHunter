import glob
import warnings
import sys
import os
import json
import subprocess
import warnings
from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np
from specutils import Spectrum1D

"""
This module handles calling SNID-SAGE and store results in a /snid_results directory
and provides functions for processing one spectra at a time or run multiple at once.

We will be running batch analysis for the purposes of this analysis.

Developer's Notes for Future Iterations:
Look into forcing a range rather than a strict redshift, ask around for user expereince,
-- forced redshfit z+0.005, z-0.005
"""

def run_SNID_SAGE(filepath, z = None):
    """
    Run SNID-SAGE on a single spectrum and prints results in /snid_results directory
    Including template and object spectrum as text fiels, and diagnostic plots as .png files
    Summary of results saved as .output by default 
    -----------------------------------------
    Params:
    
     - filepath (string): filepath of spectrum 
     - z (float, optional): redshift (if known) of the SN

    Returns: Output from SNID-SAGE CLI command run (string)
    """
    #check for redshift
    if z is not None:
        result = subprocess.run(["sage", filepath, "--forced-redshift", f"{z}", "--output-dir", "results/", "--complete"], capture_output=True, text=True)
    else:
        result = subprocess.run(["sage", filepath, "--output-dir", "results/", "--complete"], capture_output=True, text=True)

    print(result.stdout)
    return None

def run_SNID_SAGE_batch(filepath, z = None):
    """
    Runs SNID-SAGE on ALL available spectra using

    Batch processing (default saves per-object summary plus standard batch outputs)

    All results stored in /snid_results, in which each individual spectrum's ouput 
    saved in a subdirectory with the filename

    Batch results saved in a machine-readable .csv file: "batch_results.csv"
    Human-friendly summary saved in in a .txt file: "batch_analysis_report.txt"
    -----------------------------------------
    Params:

     - filepath (string): filepath of spectra 
     - z (float, optional): redshift (if known) of the SN

    Returns: None
    """

    env = os.environ.copy()
    env["MPLBACKEND"] = "Agg"  # force a non-interactive backend to reduce 'tight layout' warning from SNID-SAGE
    env["PYTHONUNBUFFERED"] = "1" #force it to be real-time
    
    #check for redshift 
    if z is not None:
        # run sage batch command with forced redshift
        process = subprocess.Popen(["sage", "batch", filepath,"--forced-redshift", f"{z}", "--brief", "--complete", "--output-dir", "snid_results/"], 
                                   stdout=subprocess.PIPE,  # catch the output
                                   stderr=subprocess.STDOUT,
                                   text=True, 
                                   bufsize=1,
                                   env = env) #send line-by-line

    else:
        # run sage batch command with default redshift range
        # --complete: ensures the spectrum + template spectrum are returned
        process = subprocess.Popen(["sage", "batch", filepath, "--complete", "--brief", "--output-dir", "snid_results/"], 
                                   stdout=subprocess.PIPE,  # catch the output
                                   stderr=subprocess.STDOUT,
                                   text=True, 
                                   bufsize=1,
                                   env=env) #send line-by-line

    # Stream and Filter
    try:
        # Stream output in real-time
        for line in iter(process.stdout.readline, ''):
            clean_line = line.strip()
            
            # Filter out known noise
            if not clean_line or "tight_layout" in clean_line or "RuntimeWarning" in clean_line:
                continue
            
            # Only print the progress lines or the summary
            # Progress lines start with [X/Y], Summary starts with 'Starting' or 'Done'
            if clean_line.startswith('[') or clean_line.startswith('Starting') or clean_line.startswith('Done'):
                print(clean_line)
                sys.stdout.flush() # Ensure it hits your screen immediately
                
    except KeyboardInterrupt:
        process.kill()
        print("\nProcess interrupted by user.")
    finally:
        process.wait()
        
    return None

def print_snid_results():
    """
    Print SNID-SAGE .output for user convinience
    -----------------------------------------
    Params:
    - filename (string): filepath for the .output summary

    Returns: None
    """
    filename = "snid_results/batch_analysis_report.txt"

    try:
        with open(filename, 'r') as file:
            content = file.read()
            print(content)
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")

    return None

def get_obs_date(filenames):
    """
    Finds the date of observation from spectrum file name. 
    Handles the folowing formats: YYYY-MM-DD, YYYYMMDD, JD.
    -----------------------------------------------------------
    Params:
    - filenames (string): list of file names to search through

    Returns: an array of dates for each file
    """
    # get date of observation from filenames (standard convention for SN spectrum filenames)

    #Look for a pattern in the filename that matches YYYY-MM-DD or YYYYMMDD
    date_pattern = re.compile(r'(\d{4}-\d{2}-\d{2})|(\d{8})|(\d{7}.)')
    # ( \d{4}-\d{2}-\d{2} )  -> Matches YYYY-MM-DD
    # ( \d{8} )              -> Matches YYYYMMDD (8 digits)
    # ( \d{7}. )             -> Matches JD format (7digits) and a decimal
    
    #get an array of dates from filename info
    date = np.array([])
    
    for name in filenames:
        match = date_pattern.search(name)
        if match:
            # result is whichever group (1, 2, or 3) found a hit
            date_str = match.group(0)
    
            #convert JD to YYYY-MM-DD format 
            if date_str == match.group(3):
                t = Time(date_str, format='jd')
                date_str = t.to_value('iso', subfmt='date')
        
            date = np.append(date, date_str)

    return date

def analyze_output(filepath):
    """
    Calls following functions to analyze batch_reslts.csv

    Params: 
    - filepath (string): location of batch_results.csv

    Returns: sucess_df (pandas dataframe): relevant data, cleaned and chronologically organized
    """
    
    # Compile relavant SNID-SAGE spectral data sorted by date of observation 
    result_df = runSNIDsage.sort_spectra("snid_results/")

    # Report how many spectra SNID-SAGE successfully analyzed 
    success_df = runSNIDsage.check_sucess(result_df)
    
    return success_df
    
def sort_spectra(filepath):
    """
    This function performs the following:
    Copies relevant info from SNID-SAGE output into a dataframe, 
    sorted chronologically by observation date
    ---------------------------------------------------------------
    Params:
    - filepath (string): points to batch_results.csv from SNID-SAGE

    Returns: result_df (pandas dataframe) refined, and chronologically sorted spectral data.
    """
    # read in batch_results.csv
    batch_results = pd.read_csv(filepath + "batch_results.csv")
    
    # get filenames for the spectra
    filenames = np.array(filenames = np.array(batch_results["file"]))
                         
    # get observation dates from filenames and add a corresponding column to the dataframe
    date = get_obs_date(filenames)
    
    batch_results["date"] = pd.to_datetime(date) #pd.datetime object for sorting
    
    #construct a dataframe of relevant info
    result_df = pd.DataFrame({"file": batch_results["file"],
                          "date": batch_results["date"],
                          "type": batch_results["type"],
                          "subtype":batch_results["subtype"],
                          "match_quality": batch_results["match_quality"],
                          "best_template": batch_results["best_template"],
                          "type_confidence": batch_results["type_confidence"],
                          "second_best_type": batch_results["second_best_type"],
                          "subtype_confidence":batch_results["subtype_confidence"],
                          "second_best_subtype": batch_results["second_best_subtype"],
                          "z": batch_results["z"],
                          "Q_cluster": batch_results["Q_cluster"],
                          "success": batch_results["success"],
                          "error": batch_results["error"]
                         })
    #sort by date 
    result_df = result_df.sort_values(by="date", ascending=True) #sort from oldest to newest

    return result_df 

def check_success(result_df):
    """
    Check how many spectra SNID-SAGE successfully classified
    Print Statistics, and any errors explaining failures
    ---------------------------------------------------------
    Params:
    - result_df (pandas dataframe): spectral data to search through

    Returns: 
    """
    # Check for success 
    success_100_percent = result_df["success"].all()
    # # .all() returns True (bool) only if all values in a column are True(bool)
    
    if success_100_percent:
        print("All spectra successfully analyzed!")
        print("#" * 50)
        
    else:
        #report percent success    
        success_dates = np.array(result_df.loc[result_df["success"] == True, "date"])
        errors = np.array(result_df.loc[result_df["success"] == False, "error"])
    
        total_spectra = len(success_dates) + len(errors)
        percent_success = (len(success_dates)/total_spectra) * 100
        
        print(f"Analyis succeeded for {percent_success:.1f}% of spectra. \n")
        print(f"{len(errors)}/{total_spectra} failed in analysis...\n")
         
        
        #report errors
        print("ERRORS:")
        print("#" * 50)
    
        files = np.array(result_df.loc[result_df["success"] == False, "file"])
        dates = np.array(result_df.loc[result_df["success"] == False, "date"])
    
        no_matches = np.array([])
        failures = np.array([])
    
        for err in errors:
            if err == "No good matches found":
                no_matches = np.append(no_matches, err)
            else:
                failures = np.append(failures, err)
    
        if len(no_matches) != 0:
            print(f"For the following {len(no_matches)} spectra, no good matches were found:")
            for i in range(len(errors)):
                if errors[i] == "No good matches found":
                    print(f"{files[i]}: {errors[i]}")
            print("(These spectra had no good template matches - this is a normal analysis outcome)")
            
        if len(failures) != 0:
            print(f"\nThe following {len(failures)} spectra, failed due to processing errors:")
            for i in range(len(errors)):
                if errors[i] != "No good matches found":
                    print(f"{files[i]}:{errors[i]}")


    success_df = result_df[result_df['success']] 
    
    return success_df
