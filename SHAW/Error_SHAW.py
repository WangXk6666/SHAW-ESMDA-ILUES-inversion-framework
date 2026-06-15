from General.draw_prior_sample import PriorSampler as draw
from SHAW.SHAW_exe import Shaw
from SHAWParRewrite import ParaRewrite as rewrite
from SHAWSimRead import SimResultReader as Reader
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
class CheckError:
    def __init__(self, param_range, mapping, relevant_headers,N_iter):
        self.param_range = param_range
        self.relevant_headers = relevant_headers
        self.mapping = mapping
        self.N_iter = N_iter
    def Abnormal_end_Error(self, abnormal_end, work_dir, rewrite_path, exe_path, thread_id):
        i = 1
        Alterative_param = None
        while abnormal_end:
            N_e = 1
            DrawParam = draw.draw_samples(self.param_range, N_e)
            Alterative_param = DrawParam[:, 0]
            rewrite.rewrite(rewrite_path, Alterative_param, self.mapping)
            success, message, abnormal_end = Shaw.execute(thread_id, exe_path, work_dir)
            i += 1
            if i>=100:
                logging.critical(f"{thread_id} terminated abnormally and reached the maximum number of attempts."
                                 f"Please check the relevant settings")
        return Alterative_param
    def Results_length_Error(self,actual_data_points,N_obs,thread_id,idx, thread_work_dir,thread_SIT_path,thread_exe_path,
                             obs_type, outer_iter):
        i = 0
        alternative_param = None
        Y = None
        Another_Y = None
        while actual_data_points != N_obs:
            i += 1
            alternative_param = self.Abnormal_end_Error(
                True,
                thread_work_dir,
                thread_SIT_path,
                thread_exe_path,
                thread_id,
            )
            SHAWSimReader = Reader(thread_work_dir, self.relevant_headers)
            Y, Another_Y = SHAWSimReader.ReadSimData(obs_type, thread_work_dir, self.N_iter, outer_iter, idx)
            actual_data_points = len(Y)
            if i > 100: logging.critical(f"{thread_id} terminated abnormally and reached the maximum number of attempts."
                                 f"Please check the relevant settings")
        return alternative_param,Y,Another_Y,actual_data_points
if __name__ =='__main__':
    pass