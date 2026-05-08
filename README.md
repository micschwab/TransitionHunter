# Transition Hunter
**Transition Hunter** is a tool to identify transitions in spectral classification during the evolution of a supernova (SN). To identify spectra, it utilizes the SuperNova IDentification – Spectral Analysis and Guided
Exploration (SNID–SAGE)(Stoppa & Smartt 2026), which builds upon the original SNID (Blondin and Tonry 2007) using cross-correlation techniques to match SN spectra to templates (SN spectra with known classifications),
with the addition of modern clustering for spectral classification choice. **Transition Hunter** reads the results of SNID-SAGE analysis for all SN spectra provided and/or queried for using WISeREP_API (Müller-Bravo 2023) 
analyzes the output to determine whether or not a transition in spectral identification may have occurred in the evolution of a given supernova to aid in spectral analysis.  

## Installation
#### Virtual Environment (Recommended)
Create a virtual environment 
```
conda create --name transitionHunter python pip jupyter
conda activate transitionHunter
```
#### Install all Requirements
```
pip install -r requirements.txt
```
Install SNID-SAGE & WISeREP_API
```
pip install snid-sage
pip install wiserep_api
```
# Setup
### Clone the repository 
Clone the GitHub repository 
```
git clone git@github.com:micschwab/TransitionHunter.git
```
### Providing Spectra 
If you want to analyze spectra already downloaded onto your local machine, copy all files into a /spectra folder within the main directory
```
cd TransitionHunter/
mkdir spectra
cd spectra
cp -p ~/path_to_desried_files/* .
```
If you choose to download spectra by querying WISeREP, downloaded files will be added to this folder. 
If you choose not to provide any spectra and instead only query WISeREP, this folder will be created for you.

### Supported Data Formats

- FITS files (.fits, .fit)
- ASCII tables (.dat, .txt, .ascii, .asci, .csv, .flm)

### Running TransitionHunter
From your command line (using python or ipython) or in a jupyter notebook run TransitionHunter in the main directory
```
#import 
from run import run_TranistionHunter

#example usage:
run_TransitionHunter('SN_name') # example run, SNID-SAGE

run_TransitionHunter('SN_name', z = 0.07) # example run, with redshift if known, may improve SNID-SAGE results by forcing the reshift to the known value 

run_TranistionHunter('SN_name', searchWiserep=True, z =0.07) #query WISeREP & force redshift

```

### Clean Up/Running Multiple Times
If you have already completed one analysis, you must move or rename the tansition.log file and the following folders: /raw, /spectra, and /snid_results.
We recommend moving them into a folder with the same name as the SN.
```
mkdir SN_name
mv raw/ spectra/ snid_results/ SN_name/
mv transition.log SN_name/
```