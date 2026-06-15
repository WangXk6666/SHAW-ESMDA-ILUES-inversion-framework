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
        work_dir = str(input('where is work_dir?'))
        # obs_type可选类型如下:
        """
            obs_type可选类型如下:
                : param temp:温度
                : param moi:液态含水量
                : param mat:基质势
                : param ET:蒸散发
                : param solute:溶质
                : param total_salt:总盐
        """
        obs_type = 'moi'
        choose_index = 'r2'
        N_other_pars = 0
        beta = 1
        confidence_level = 0.95
        curve_type = 3
        obs_sd= float(input('obs_sd = ?'))
        N_e = int(input('N_e = ?'))
        N_iter = int(input('N_iter = ?'))
        alpha = float(input('alpha = ?'))
        N_threads = int(input('N_thread = ?'))
        Soil = str(input('Soil = ?'))
        N_layer = int(input('N_layer = ?'))
        N_PLANT = 1
        Residue = True
        Stewart_Jarvis = True
        N_par,par_name,param_range,mapping,couple=P.differentlayer(Soil)
        da = main(work_dir, N_e, N_iter, alpha, N_par, N_other_pars, beta, param_range,
                  'K', obs_type,curve_type, obs_sd, N_layer, N_threads,
                  confidence_level, N_PLANT, Residue, mapping, Stewart_Jarvis, par_name,couple)
        da.run(choose_index)
if __name__ == '__main__':
    runner = RUN()
    runner.run()