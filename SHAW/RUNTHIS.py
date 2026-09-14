"""
================================================================================
SHAW-ESMDA-ILUES Framework

Author: Xueke Wang
Affiliation: School of Water and Environment, Chang'an University
E-mail: WangXk6666@outlook.com

Description:
    This framework couples the Simultaneous Heat and Water (SHAW) model with
    ensemble smoother multiple data assimilation (ESMDA) and iterative local
    updating ensemble smoother (ILUES) for parameter estimation and uncertainty
    quantification in seasonal freeze–thaw SPAC systems.

    The framework is developed for investigating parameter identifiability,
    posterior hydrothermal state simulation, and uncertainty propagation under
    limited observational constraints.

Version: 1.0

Date: September 2026

Copyright: Copyright (c) 2026 Xueke Wang and collaborators.

License:
    This code is provided for academic and non-commercial research purposes.
    Users should cite the associated publication when using this framework.

Third-party models and methods:
    1. SHAW model:
       Flerchinger, G. N., and Saxton, K. E. (1989).
       Simultaneous heat and water model of a freezing snow-residue-soil system.
       I. Theory and development.
       Transactions of the ASAE, 32(2), 565–571.

    2. ESMDA:
       Emerick, A. A., and Reynolds, A. C. (2013).
       Ensemble smoother with multiple data assimilation.
       Computers & Geosciences, 55, 3–15.

    3. ILUES:
       Zhang, J., et al. (2018).
       Iterative local updating ensemble smoother for parameter estimation
       of highly nonlinear systems.
       Water Resources Research.

================================================================================
"""



import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.resolve()))
from math import gamma
import numpy as np
from TIMECOUNT import TIME
from MAINPROGRESS import  main
from P import P

class RUN:
    def __init__(self):
        pass
    @TIME.time_it
    def run(self):
        work_dir = r"C:\Users\11262\Desktop\SHAW-ESMDA-ILUES-inversion-framework-main\TEST_SHAW"
        obs_type = 'moi' # moi is liquid water content
        beta = 1 # Weight of J
        confidence_level = 0.95 # Posterior interval
        curve_type = 3 # 3 is Campbell curve
        obs_sd= 0.02 # Observation error
        N_e = 20 # Ensemble size
        N_iter = 1 # Iteration times
        alpha = 0.1 # Local fraction
        N_threads = 2 # Number of threads
        Soil = '5 layers' # Number of soil layers
        N_PLANT = 1 # Number of plant specices
        Residue = True # Residue is considered
        Stewart_Jarvis = True # Stewart_Jarvis equation is considered
        N_par,N_layer,par_name,param_range,mapping,couple=P.differentlayer(Soil)
        da = main(work_dir, N_e, N_iter, alpha, N_par, beta, param_range,
                  'K', obs_type,curve_type, obs_sd, N_layer, N_threads,
                  confidence_level, N_PLANT, Residue, mapping, Stewart_Jarvis, par_name,couple)
        da.run()
if __name__ == '__main__':
    runner = RUN()
    runner.run()