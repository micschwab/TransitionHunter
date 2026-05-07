# Transition Hunter
**Transition Hunter** is a tool to identify transitions in spectral classification during the evolution of a supernova (SN). To identify spectra, it utilizes the SuperNova IDentification – Spectral Analysis and Guided
Exploration (SNID–SAGE)(Stoppa & Smartt 2026), which builds upon the original SNID (Blondin and Tonry 2007) using cross-correlation techniques to match SN spectra to templates (SN spectra with known classifications),
with the addition of modern clustering for spectral classification choice. **Transition Hunter** reads the results of SNID-SAGE analysis for all SN spectra provided and/or queried for using WISeREP_API (Müller-Bravo 2023) 
analyzes the output to determine whether or not a transition in spectral identification may have occurred in the evolution of a given supernova to aid in spectral analysis.  

## Installation
#### Virtual Environment (Recommended)
Create a virtual environment and install all requirements
```
conda create --name transitionHunter python pip jupyter
conda activate transitionHunter
pip install -r requirements.txt

```
Install SNID-SAGE 
```
pip install snid-sage
```
Install WISeREP_API
```
pip install snid-sage
```
