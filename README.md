# cogen_eval
## Uncertainty Quantification in the energy management of a CHP system

In this repository you will find all the script to reprosuce the results of the paper:

*L. Giaccone, P. Lazzeroni and M. Repetto "Uncertainty Quantification in Energy Management Procedures"
(Currently under review)*

## Requirements

Codes included in this repository are written in Python 3, that is the only real requirement. They have been tested with Python 3.7 and 3.8 but also earlier version of Python 3 should work.

Polynomial Chaos Exapansion simulation are made using this module [https://github.com/giaccone/pce](https://github.com/giaccone/pce) that is developed by the same author of this repository. This module can deployed throug the Python Package Index, therefore, it can be easily obtained bu rinning the following command:

```bash
pip install pce
```


## Content of the repository

1. `cogen_util.py`: this file provide include two function that are used in other files. This file is not directely used by the user.
2. `CogenEval_PCE_vs_MC.py`: this file perform an uncertaninty analysis with PCE and MC and provide the comparison in the form of a plot. The user can set uniform or normal distribution and decide if the results are saved in npz (numpy) format
3. `CogenEval_Sobol_indices.py`: this file computes Sobol indices for the case study under analysis. The user can set uniform or normal distribution and decide if the results are saved in npz (numpy) format.
4. `plot_input_profiles.py`: this file plots the input profile of the thermal energy demand and the electricity cost
5. `plot_pce_vs_mc.py`: this file plot the results obtained at point 2 (if the user saved them in npz format)
6. `plot_sobol.py`: this file plot the results obtained at point 3 (if the user saved them in npz format)


