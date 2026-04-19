import glob
import os
import json
from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np
from specutils import Spectrum1D
"""
This Module will analyze SNID results and confirm any/all transitions by saving it to transitionlog.csv

? How to handle featureless blue continuum.
-->  see what snid outputs, read how it interprets it. 
"""

#Print whether or not a transition has occured 


# record novel identifications, epoch identified, and confidence in identification. save to transitionlog.csv 