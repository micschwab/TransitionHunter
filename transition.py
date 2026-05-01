import glob
import os
import pandas as pd
import json
from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np
from specutils import Spectrum1D

"""
This Module will analyze SNID results and confirm any/all transitions 

Output saved it to transitionlog.csv

? How to handle featureless blue continuum.
-->  see what snid outputs, read how it interprets it. 

"""

#read in SNID-SAGE results
pd.read_csv("/results/batch_results.csv")

#Analyze the output for novel Identifications


# record novel identifications, epoch identified, and confidence in identification. save to transitionlog.csv 