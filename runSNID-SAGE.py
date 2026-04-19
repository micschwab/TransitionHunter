import glob
import os
import json
from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np
from specutils import Spectrum1D
"""
This Module will be calling SNID and storing/plotting results
"""

## test with SN2025vzq data 

# # Single spectrum analysis (templates auto-discovered). Saves the summary (.output) by default
# sage data/SN2018bif.csv -o results/

# # Batch processing (default saves per-object summary plus standard batch outputs)
# sage batch "data/*.dat" -o results/

# # Batch from a CSV list with per-row redshift (if provided)
# sage batch --list-csv "data/spectra_list.csv" -o results/