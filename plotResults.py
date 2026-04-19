import glob
import os
import json
from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np
from specutils import Spectrum1D
"""
This Module will perform basic plotting and style for diagnositc plots
"""

#plots to make dependednt on SNID output. 


# From SNID results/tranistionlog.csv

#idea: Id-type vs epoch to show changes in trends 
# --> plot reported epochs' SN IDs, along with their best-fitting SN spectral template
# --> Plot of the SN’s spectral evolution, distinguished by SNID–SAGE classification in both color and marker

