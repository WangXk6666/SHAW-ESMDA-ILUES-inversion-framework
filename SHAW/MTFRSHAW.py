import threading
import numpy as np
import shutil
import os
import sys
from tqdm import tqdm
from SHAW.SHAW_exe import Shaw
from SHAWParRewrite import ParaRewrite
from SHAWSimRead import SimResultReader
from General.draw_prior_sample import PriorSampler
from General.CriticalError import CriticalError
from General.obs_read import obs_read
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
class MTFRSHAW:
    def __init__(self, base_work_dir, param_range, N_e, length_of_obs, N_iter, parameters, outer_iter):
        self.base_work_dir = os.path.join(base_work_dir, 'Model')
        self.param_range = param_range
        self.N_e = N_e
        self.N_obs = length_of_obs
        self.N_iter = N_iter
        self.parameters = parameters
        self.outer_iter = outer_iter
        self.Another_Result = np.full((self.N_obs['N12'], self.N_e), np.nan)
        self.SimData = np.full((self.N_obs['N11'],self.N_e), np.nan)
        self.results = []
        self.lock = threading.Lock()
        self.dir_lock = threading.Lock()
        self.error_count = 0
        self.abnormal_count = 0
        self.critical_error_occurred = threading.Event()
        self.critical_error_message = None
        self.progress_lock = threading.Lock()

    def _copy_essential_files(self, model_base_dir, thread_id):
        thread_work_dir = os.path.join(model_base_dir, f"thread_{thread_id}")
        os.makedirs(thread_work_dir, exist_ok=True)
        essential_files = ["INPUT.INP", "SHAW303", "SIT.INP", "WEATHER.INP", "TEMPERATURE.INP", "MOISTURE.INP"]
        for file in essential_files:
            src = os.path.join(model_base_dir, file)
            dst = os.path.join(thread_work_dir, file)
            if not os.path.exists(src):
                logging.warning(f"源文件不存在，跳过复制: {src}")
                continue
            try:
                shutil.copy2(src, dst)
                if thread_id==1:
                    logging.info(f"成功复制文件到线程{thread_id}：{file}")
            except Exception as e:
                logging.error(f"复制文件失败（线程{thread_id}，文件{file}）：{str(e)}")

    def _worker(self, thread_id, param_thread, obs_type, start_index, relevant_headers, mapping, progress_bar=None):
        thread_work_dir = os.path.join(self.base_work_dir, f"thread_{thread_id}")
        thread_exe_path = os.path.join(thread_work_dir,'SHAW303')
        thread_SIT_path = os.path.join(thread_work_dir, 'SIT.INP')
        num_simulations = len(param_thread)
        end_index = start_index + num_simulations
        param_updates = []
        ThreadSimData =np.full((num_simulations, self.N_obs['N11']), np.nan)
        Thread_another_Result = np.full((num_simulations,self.N_obs['N12']),np.nan)
        try:
            for idx, params in enumerate(param_thread):
                if self.critical_error_occurred.is_set():
                    logging.info(f"Thread {thread_id} detected critical error，early termination")
                    return
                Y = []
                Another_Y = []
                max_retry = 20
                retry_count = 0
                has_mistake = True
                current_params = params
                while has_mistake and retry_count <= max_retry:
                    retry_count += 1
                    if retry_count > 1:
                        current_params = PriorSampler.draw_samples(self.param_range, 1).flatten().tolist()
                        logging.info(f"Thread {thread_id} 样本{idx}第{retry_count}次重试，抽取新参数: {current_params}")
                    with self.dir_lock:
                        os.chdir(thread_work_dir)
                    ParaRewrite.rewrite(thread_SIT_path, current_params, mapping)
                    try:
                        _,_,_ = Shaw.execute(thread_id, thread_exe_path, thread_work_dir)
                        SHAWSimReader = SimResultReader(thread_work_dir, relevant_headers)
                        Y, Another_Y = SHAWSimReader.ReadSimData(obs_type, thread_id,self.N_iter, self.outer_iter, idx)
                        print(len(Y), Another_Y,self.N_obs['N11'], self.N_obs['N12'])
                        if len(Y) == self.N_obs['N11']:
                            has_mistake = False
                        else:
                            has_mistake = True
                            print('模型1出错')
                        if has_mistake:
                            if retry_count == 1:
                                with self.lock:
                                    self.abnormal_count += 1
                            if retry_count >= max_retry:
                                logging.error(f"Thread {thread_id} 样本{idx}重试{max_retry}次仍失败，标记为执行错误")
                                with self.lock:
                                    self.error_count += 1
                                break
                    except CriticalError as ce:
                        with self.lock:
                            if not self.critical_error_occurred.is_set():
                                self.critical_error_occurred.set()
                                self.critical_error_message = f"Thread {thread_id} encountered a critical error: {ce}"
                        logging.info(f"Thead {thread_id} encountered a critical error: {ce}")
                        return
                    except Exception as e:
                        logging.info(f"Error occurred while thread {thread_id} was running {idx}: {str(e)}")
                        with self.lock:
                            self.error_count += 1
                        has_mistake = True
                        continue

                global_idx = start_index + idx
                param_updates.append((global_idx, current_params))
                ThreadSimData[idx] = Y
                Thread_another_Result[idx] = Another_Y
                if progress_bar:
                    with self.progress_lock:
                        progress_bar.update(1)

            if ThreadSimData.shape[0] > 0:
                with self.lock:
                    self.SimData[:self.N_obs['N11'], start_index:end_index] = ThreadSimData.T
                    self.Another_Result[:self.N_obs['N12'], start_index:end_index] = Thread_another_Result.T
            if param_updates:
                with self.lock:
                    for global_idx, alternative_param in param_updates:
                        self.parameters[:, global_idx] = alternative_param
        except Exception as e:
            with self.lock:
                if not self.critical_error_occurred.is_set():
                    self.critical_error_occurred.set()
                    self.critical_error_message = f"Thread {thread_id} encountered an unprocessed error: {e}"
            logging.info(f"Thread {thread_id} encountered an unprocessed error: {e}")
        finally:
            with self.dir_lock:
                os.chdir(self.base_work_dir)

    def MTFRSHAW(self, N_threads, obs_type, relevant_headers, mapping, show_progress=True):
        self.results = []
        self.error_count = 0
        self.abnormal_count = 0
        self.critical_error_occurred.clear()
        self.critical_error_message = None
        for i in range(1,N_threads+1):
            self._copy_essential_files(self.base_work_dir, i)
        progress = tqdm(total=self.N_e, desc="Run simulation") if show_progress else None
        threads = []
        if self.N_e % N_threads != 0:
            raise ValueError(f"N_e ({self. N_e}) cannot be divided by N_threads ({N_threads})")
        N_e_thread = self.N_e // N_threads
        start_index = 0
        for i in range(1, N_threads + 1):
            num_tasks = N_e_thread
            if num_tasks == 0:
                continue
            param_slice = self.parameters[:, start_index:start_index + num_tasks]
            param_thread = [param_slice[:, j].tolist() for j in range(num_tasks)]
            current_start = start_index + 1
            current_end = start_index + num_tasks
            thread = threading.Thread(
                target=self._worker,
                args=(i, param_thread, obs_type, start_index, relevant_headers, mapping, progress),
                name=f"Worker-{i}",
                daemon=True
            )
            threads.append(thread)
            thread.start()
            if i == 1:
                logging.info(f"Thread {i} is started (processing simulation  {current_start}~{current_end}）")
            start_index += num_tasks
        for i, thread in enumerate(threads):
            thread.join()
            if i == N_threads - 1: 
                logging.info(f"All threads have been finished")
        if self.critical_error_occurred.is_set():
            logging.info(f"Encountering critical errors: {self.critical_error_message}")
            sys.exit(1)
        if show_progress and progress:
            progress.close()
        np.savetxt(os.path.join(os.path.dirname(self.base_work_dir), 'Ensemble/Total_Sim_Results.csv'),
                   self.SimData.astype(float), delimiter=',', fmt='%.5f')
        np.savetxt(os.path.join(os.path.dirname(self.base_work_dir), 'Ensemble/updated_parameters.csv'),
                   self.parameters, delimiter=',', fmt='%.5f')
        success_count = self.N_e - self.error_count
        logging.info(f"Successed: {success_count}次")
        logging.info(f"Initial abnormal termination: {self.abnormal_count}次")
        logging.info(f"Execution error: {self.error_count}次")
        logging.info(f'=====================================Finish running=========================================\n')
        logging.info(f'                               第{self.outer_iter}次迭代的模型计算已全部完成                    \n')
        logging.info(f'=============================================================================================')
        return self.parameters, self.SimData, self.Another_Result
if __name__ == "__main__":
    pass
