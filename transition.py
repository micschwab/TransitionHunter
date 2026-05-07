import os
import re
import glob
import tabulate
import numpy as np
import pandas as pd
import json
from io import StringIO
from astropy.io import fits
import matplotlib.pyplot as plt
from specutils import Spectrum1D
import runSNIDsage

"""
This Module will analyze SNID results and confirm any/all transitions.
Diagnositc plots and analysis will be stored in a /results folder. 

Summary of results saved to transition_summary.txt

"""

def hunt(sn, success_df):
    """
    This function calls the following functions to read and analyze 
    SNID-SAGE output and determine whether or not a transition can be 
    found, and to what degree of confidence. 
    ------------------------------------------------------------------
    Params:
     - sn (string): SN name
     - sucess_df (pandas dataframe): rlevant data from spectra with successful
       SNID-SAGE analysis, orded chronologically by date of observation 

    Returns: has_transition (string): 'Y' or 'N' 
    """
    
    # Make First Quality Cut
    # # Cut identifications SNID-SAGE reported as having Low Match Quality
    to_remove = ['Very Low', 'Low'] #cut low or verly low match confidences
    confident_df = success_df[~success_df['match_quality'].isin(to_remove)]
    confident_df = confident_df.reset_index(drop=True)

    # Warn the user if you think the transition may be obscured
    template_str = 'sn' + sn
    if template_str in np.array(confident_df["best_template"]):
        print("#"*100)
        print("WARNING: TRANSITION MAY BE OBSCURED ")
        print(" -->  This supernova is being matched to itself, and is returning a static, reported classification.")
        print("#"*100)

    # Get a report of transition metrics
    report_df = get_transition_report(confident_df)

    # Determine whether or not a Transition has occured
    legit_classes = get_verdict(report_df)

    # print summary of results
    print_results(legit_classes)

    # define a boolean as to weather a transiton was found
    tranistioned = False
    
    if len(legit_classes) > 1:
        transitioned = True
    
    return transitioned
    
def get_transition_report(confident_df):
    """
    This function handles the logic of iterating through our data
    searching for a transition, recording the metrics needed for 
    our final verdict and recording them in a new dataframe.
    ----------------------------------------------
    Params:
    - confident_df (pandas data frame): Report of confident matches from SNID-SAGE output

    Returns: report_df (pandas data frame): Report of Transition Metrics
    """
    # Initialize novel IDs and record row index 
    novel_ID = np.array([]) # track type
    novel_subID = np.array([]) # track subtype
    novel_idx = np.array([]) # index of column in DF
    
    # Store lengths of every series of consequitive IDs 
    type_streaks = {} # type
    subtype_streaks = {} #subtype

    # Note Ambiguous Ids
    transition_notes = [] # flag low confidence Ids/subIds
    type_ambig_indx = []
    subtype_ambig_indx = []
    
    # Initialioze variables to remember Last IDs
    prev_ID = None
    prev_subID = None
    
    # Initialize Counters for consequtive ID
    type_counter = 0
    subtype_counter = 0
    
    # Track date, a "streak" must be over increments of 1 day or more
    track_last_date = None
    
    ####################################################################
    # Iterate to find evidence of a transition
    ####################################################################
    
    for row in confident_df.itertuples(): 
        curr_ID, curr_subID = row.type, row.subtype
        curr_date = row.date
        
        # Check whether this is a new observation 
        is_new_day = (curr_date != track_last_date)
    
        # Get confidences for the current row
        type_conf = row.type_confidence
        subtype_conf = row.subtype_confidence
        weak = ['Low', 'Very Low']
    
        # --- Check Type ---
        if curr_ID == prev_ID:
            #if the ID is not new and it's a new observation, update the streak
            if is_new_day:
                type_counter += 1
        else:
            # Save any finished streaks
            if prev_ID is not None:
                type_streaks.setdefault(prev_ID, []).append(type_counter)
            
            # Check for uniqueness
            if curr_ID not in novel_ID:
                # Log novel instance
                novel_ID = np.append(novel_ID, curr_ID)
                novel_idx = np.append(novel_idx, row.Index)
                
                # Note if low confidence
                if type_conf in weak:
                    if not pd.isna(row.second_best_type) & (row.second_best_type in novel_ID):
                        transition_notes.append(f"Type {curr_ID} is {type_conf}, "
                                                f"matches existing {row.second_best_type}.")
                        type_ambig_indx.append(row.Index)
    
            # Save type for comparison
            prev_ID = curr_ID   # Start a new streak
            type_counter = 1
    
        # --- Check Subtype ---
        if curr_subID == prev_subID:
            # If the subID is not new and it's a new observation, update the streak
            if is_new_day:
                subtype_counter += 1
        else:  
            # Save any finished subtype streaks
            if prev_subID is not None:
                subtype_streaks.setdefault(prev_subID, []).append(subtype_counter)
           
            # Check for uniqueness
            if curr_subID not in novel_subID:
                # Log novel instance
                novel_subID = np.append(novel_subID, curr_subID)
                
                # Log row index if not already logged (subtype unique but type wasn't):
                if row.Index not in novel_idx:
                    novel_idx = np.append(novel_idx, row.Index)
    
                # Perform confidence check
                if subtype_conf in weak:
                    if not pd.isna(row.second_best_subtype) & (row.second_best_subtype in novel_subID):
                        transition_notes.append(f"Subtype {curr_subID} is {subtype_conf}, "
                                                f"matches existing {row.second_best_subtype}.")
                        subtype_ambig_indx.append(row.Index)
    
            # Save type for comparison
            prev_subID = curr_subID
            subtype_counter = 1 # Start a new streak
    
        # ---- Update date -------
        track_last_date = curr_date
    
    # ------- Save the last active streaks -------------------------------
    if prev_ID: 
        type_streaks.setdefault(prev_ID, []).append(type_counter)
        
    if prev_subID: 
        subtype_streaks.setdefault(prev_subID, []).append(subtype_counter)
    
    # Create a dataframe of novel instances 
    transition_df = confident_df.iloc[novel_idx]

    #################### Perform Confidence Checks ########################
    ####################################################################
    
    # 1. Get Frequency (%)
    total_rows = len(confident_df)
    t_freq = (confident_df['type'].value_counts() / total_rows * 100).to_dict()
    s_freq = (confident_df['subtype'].value_counts() / total_rows * 100).to_dict()
    
    # 2. Get Max Streak
    t_persistence = {t: max(streaks) for t, streaks in type_streaks.items()}
    s_persistence = {s: max(streaks) for s, streaks in subtype_streaks.items()}
    
    # Modify the Transition DataFrame with these stats
    report_df = transition_df.copy()
    
    report_df['type_max_streak'] = report_df['type'].map(t_persistence)
    report_df['subtype_max_streak'] = report_df['subtype'].map(s_persistence)
    report_df['type_freq'] = report_df['type'].map(t_freq)
    report_df['subtype_freq'] = report_df['subtype'].map(s_freq)
    report_df['type_ambig'] = report_df.index.isin(type_ambig_indx)
    report_df['subtype_ambig'] = report_df.index.isin(subtype_ambig_indx)


    #################### PRINT RESULTS ########################

    # Report novel Classifications
    print(f"{len(report_df)} Novel Identifications Found...\n")
    report_df['date'] = pd.to_datetime(report_df['date']).dt.strftime('%Y-%m-%d')
    print_report_data = report_df[["date", "type", "subtype", "match_quality", "best_template", "type_confidence",
                                   "second_best_type","subtype_confidence", "second_best_subtype", "type_ambig", 
                                   "subtype_ambig"]].values.tolist()
    report_headers = ["date", "type", "subtype", "match_quality", "best_template", "type_confidence",
                      "second_best_type","subtype_confidence", "second_best_subtype", "type_ambiguous", "subtype_ambiguous"]

    print(tabulate(print_report_data, headers=report_headers, tablefmt="simple", stralign="center"))

    # Report Ambiguous Classifications
    if transition_notes:
        print(f"\n{len(transition_notes)} Ambigous Classifications:")
        print("-"*50)
        for note in transition_notes:
            print(note)
    else:
        print("No Ambigous Classifications")

    print("Identification Statistics:")

    if len(novel_ID) > 1:
        print("\nMATCHES FOUND FOR THE FOLLOWING SN TYPES:")
        print("-"* 100)
        for i in range(len(novel_ID)):
            print(f"{novel_ID[i]}: {(t_freq[novel_ID[i]]):.2f}% of spectra analyzed. Maximum of {max(type_streaks[novel_ID[i]])} consecutive identifications")
    
    if len(novel_subID) > 1:
        print("\nMATCHES FOUND FOR THE FOLLOWING SN SUBTYPES: ")
        print("-"* 100)
        for i in range(len(novel_subID)):
            print(f"{novel_subID[i]}: {(s_freq[novel_subID[i]]):.2f}% of spectra analyzed. Maximum of {max(subtype_streaks[novel_subID[i]])} consecutive identifications.")
    
    return report_df
                         
    
def get_verdict(report_df):
    """
    Reads the report_df and appliesour logic to determine 
    whether or not a transition has occured.

    Params:
    - report_df (pandas dataframe): data including metrics for determining a transition

    Returns: legit_classes (pandas dataframe): dataframe of legitimate classifications
    
    """
    verdict_df = report_df.copy()
    verdict_df["verdict"] = "N"
    verdict_df["confidence"] = "Low"

    # Iterate through the report dataframe 
    # using range to look back at the previous row
    
    for i in range(len(verdict_df)):
        row = verdict_df.iloc[i]
        
        # Check if it's the first row, or if the type has changed from the previous row
        if i == 0 or row["type"] != verdict_df.iloc[i-1]["type"]:
            # This is a TYPE transition
            # Check type metrics
            streak = row["type_max_streak"]
            ambig = row["type_ambig"]
            freq = row["type_freq"]
        
        else:
            # The type is the same as the previous row so this is a SUBTYPE transition
            # Check subtype metrics
            streak = row["subtype_max_streak"]
            ambig = row["subtype_ambig"]
            freq = row["subtype_freq"]
    
        # Apply conditions for transition
        # # Streak must be 2+ AND Ambiguity must be False
        legit = (streak >= 2) & (not ambig)
    
        # Assign values to the report dataframe
        if legit:
            verdict_df.at[verdict_df.index[i], "verdict"] = "Y"
        
            # Set confidence based on streak
            if (streak >= 5) & (freq > 10.0):
                verdict_df.at[verdict_df.index[i], "confidence"] = "High"
            else:
                verdict_df.at[verdict_df.index[i], "confidence"] = "Medium"
        else:
            # Default is already N / Low, but we'll be explicit for clarity
            verdict_df.at[verdict_df.index[i], "verdict"] = "N"
            verdict_df.at[verdict_df.index[i], "confidence"] = "Low"

    
    # Save Legitimate Classifications
    legit_classes = verdict_df[verdict_df["verdict"] == "Y"]
    legit_classes = verdict_df.reset_index(drop=True)
    
    return legit_classes

def print_results(legit_classes):
    """
    Reads classifications that have passed our
    criterea and print a summary of the results.
    
    Params:
        - legit_classes (pandas dataframe): valid classifications
        
    Returns: None
    """
    print("\nSUMMARIZING RESULTS... ")

    if len(legit_events) == 0:
        # No classification passed confidence checks
        print("\nNO TRANSITION FOUND")
        print("No SN ID passed confidence checks.")
        print("This may occur if SNID-SAGE classifications are ambiguous or if there are no consecutive identifications in the SN evolution.")
        
    elif len(legit_events) == 1:
        # No transition occured, only one classification passed confidence checks
        print("\nNO TRANSITION FOUND: 1 confident classification\n")
        table_data = legit_events[["type","subtype", "confidence"]].values.tolist()
        headers = ["TYPE", "SUBTYPE", "CONFIDENCE"]
        print(tabulate(table_data, headers=headers, tablefmt="simple", stralign="center"))
    
    elif len(legit_events) > 1:
        # transition found! 
        print(F"TRANSITION FOUND: {len(legit_events)} confident classification\n")
        table_data = legit_events[["date", "type", "subtype", "confidence"]].values.tolist()
        headers = ["DATE","TYPE", "SUBTYPE", "CONFIDENCE"]
        print(tabulate(table_data, headers=headers, tablefmt="simple", stralign="center"))

    return None
