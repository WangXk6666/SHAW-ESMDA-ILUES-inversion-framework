import numpy as np
from WaterBalanceReader import WaterBalanceReader as WBR
from SingleResultReader import SingleResultReader as SlR
from SoluteReader import SoluteResultReader as SRR
import os

class SimResultReader:
    def __init__(self,work_dir, relevant_headers):
        self.work_dir = work_dir
        self.sim_temp_path = os.path.join(self.work_dir,'TEMPERATURE.OUT')
        self.sim_moi_path = os.path.join(self.work_dir,'LIQUID.OUT')
        self.sim_matric_path = os.path.join(self.work_dir,'MATRIC.OUT')
        self.relevant_headers = relevant_headers

    def ReadSimData(self,obs_type,thread_id, N_iter, out_iter, inner_iter):
        Reader_1 = SlR(self.sim_temp_path, self.sim_moi_path, self.sim_matric_path, self.relevant_headers['temp_headers'],
                       self.relevant_headers['moi_headers'], self.relevant_headers['mat_headers'])
        Reader_2 = WBR(self.work_dir)
        Reader_3 = SRR(self.work_dir)

        if obs_type == 'temp':
            Result = Reader_1.read_sim_temp()
            Another_result = None if out_iter < N_iter else Reader_1.read_sim_moi()

        elif obs_type == 'moi':
            Result = Reader_1.read_sim_moi()
            Another_result = None if out_iter < N_iter else Reader_1.read_sim_temp()

        elif obs_type == 'mat':
            Result = Reader_1.read_sim_matric()
            Another_result = None if out_iter < N_iter else Reader_1.read_sim_temp()

        elif obs_type == 'solute':
            Result = Reader_3.read_sim_data(thread_id, out_iter, inner_iter,obs_type,
                                                        self.relevant_headers['solute_headers'])
            Another_result = None if out_iter < N_iter else Reader_1.read_sim_moi()

        elif obs_type == 'total_salt':
            Result = Reader_3.read_sim_data(thread_id, out_iter, inner_iter, obs_type,
                                                        self.relevant_headers['total_salt_headers'])
            Another_result = None if out_iter < N_iter else Reader_1.read_sim_moi()

        elif obs_type == 'ET':
            Result = Reader_2.get_result(obs_type)
            Another_result = None if out_iter < N_iter else Reader_1.read_sim_moi()

        else:
            valid_options = ("['moi', 'temp', 'mat', 'ET', 'solute', 'total_salt']")
            raise ValueError(f"obs_type must be one of {valid_options}; the current value is '{obs_type}'")
        return Result, Another_result