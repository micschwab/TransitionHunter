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
This module handles calling SNID-SAGE and store results in a /results directory
and provides functions for processing one spectra at a time or run multiple at once.

To search for a transition, we will be running batch analysis. 

Developer Note:
Look into forcing a range rather than a strict redshift, ask around for user expereince,
-- forced redshfit z+0.005, z-0.005
"""

def run_SNID_SAGE(filepath, z = None):
    """
    Run SNID-SAGE on a single spectrum and prints results in /results directory
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

    All results stored in /results, in which each individual spectrum's ouput 
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
        process = subprocess.Popen(["sage", "batch", filepath,"--forced-redshift", f"{z}", "--brief", "--complete", "--output-dir", "results/"], 
                                   stdout=subprocess.PIPE,  # catch the output
                                   stderr=subprocess.STDOUT,
                                   text=True, 
                                   bufsize=1,
                                   env = env) #send line-by-line

    else:
        # run sage batch command with default redshift range
        # --complete: ensures the spectrum + template spectrum are returned
        process = subprocess.Popen(["sage", "batch", filepath, "--complete", "--brief", "--output-dir", "results/"], 
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
    filename = "results/batch_analysis_report.txt"

    try:
        with open(filename, 'r') as file:
            content = file.read()
            print(content)
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")

    return None

def sort_spectra():
    """
    Sort spectra by epoch, for evolutionary analysis 
    Read SNID-SAGE batch_results.csv

    Write a csv sorted by epoch with "relevant information" to
    transition and evolution to be analyzed.
    """
    batch_results = pd.read_csv("/results/batch_results.csv")
    
    pass

