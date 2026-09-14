from operator import length_hint
import numpy as np
from pathlib import Path
import shutil
from General.draw_prior_sample import PriorSampler
from General.ES_K_update import ES
from General.local_update_for import LocalUpdate as ILUES
from MTFRSHAW import MTFRSHAW as MTFR
from General.obs_read import obs_read
from SHAWFinalResult.PlotResult import PlotResult as plot
from SHAWFinalResult.PlotIterationPar import IterationPloter
from SHAWFinalResult.Distribution import Relationship_of_Pars as joint_distribution
from Clear import Clear
from SHAWFinalResult.Quantile import Quantile
import logging
import csv
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class main:
    def __init__(self, work_dir, N_e, N_iter, alpha, N_par, beta, param_range, method_flag, obs_type,
                 curve_type, obs_sd, N_layer, N_threads, confidence_level, N_PLANT, Residue, mapping, Stewart_Jarvis,
                 par_name, couple):
        logging.info('——————————————————————————————————————————Begin——————————————————————————————————————————————\n')
        self.work_dir = work_dir
        self.N_e = N_e
        self.N_iter = N_iter
        self.alpha = alpha
        self.N_par = N_par
        self.beta = beta
        self.obs_type = obs_type
        self.param_range = param_range
        self.method_flag = method_flag
        self.curve_type = curve_type
        self.N_layer = N_layer
        self.N_threads = N_threads
        self.N_PLANT = N_PLANT
        self.Residue = Residue
        self.Stewart_Jarvis = Stewart_Jarvis
        self.par_name = par_name
        self.mapping = mapping
        self.couple = couple
        obs_hander_model = obs_read(Path(self.work_dir) / "Model")
        obs_1, obs_2, self.relevant_headers,self.Single_obs_type = obs_hander_model.observation(obs_type)
        self.obs = np.concatenate((obs_1, obs_2))
        # print(self.obs)
        self.length_of_obs = {'N11':len(obs_1),'N12':len(obs_2),'N00':len(obs_1)+len(obs_2)}
        # print(self.length_of_obs)
        self.obs_sd = obs_sd
        # print(self.obs_sd)
        self.C_Y = np.diag(np.full(self.length_of_obs['N11'], self.obs_sd ** 2))
        # print(self.C_Y)
        Clear.clear(self.N_threads, Path(self.work_dir)/ 'Model')
        self.Figout = Path(self.work_dir, 'Figures')
        if self.Figout.exists():
            shutil.rmtree(self.Figout)
        self.Figout.mkdir()
        self.ensemble_path = Path(self.work_dir, "Ensemble")
        if self.ensemble_path.exists():
            shutil.rmtree(self.ensemble_path)
        self.ensemble_path.mkdir()
        self.confidence_level = confidence_level
        self.initialize_ensembles()

    def initialize_ensembles(self):
        logging.info('<'*20+'Initialize the prior ensemble'+'>'*20+'\n')
        out_iter = 0
        samples = PriorSampler.load_prior_from_csv(Path(self.work_dir)/'Model'/'Prior distribution.csv')
        X = samples[:self.N_layer*5+17]
        run = MTFR(self.work_dir, self.param_range, self.N_e, self.length_of_obs, self.N_iter, X, out_iter)
        X, Y, Another_Y=run.MTFRSHAW(self.N_threads,self.obs_type, self.relevant_headers, self.mapping,show_progress=True)
        self.X_K_f=X.copy()
        self.Y_K_f=Y.copy()
        self.Another_Y_K_a=Another_Y.copy()
        self.X_KL_f=X.copy()
        self.Y_KL_f=Y.copy()
        self.Another_Y_KL_a=Another_Y.copy()
        self.C_XX = np.diag(np.diag(np.cov(self.X_KL_f)))
        self.SaveCsv(0)

    def SaveCsv(self, iter):
        base_path = Path(self.work_dir) / f"Ensemble/ensemble_{iter}"
        np.savetxt(base_path.with_name(f"{base_path.stem}_X_K_f_{self.Single_obs_type['First']}.csv"), self.X_K_f, delimiter=',', fmt='%.4f')
        np.savetxt(base_path.with_name(f"{base_path.stem}_Y_K_f_{self.Single_obs_type['First']}.csv"), self.Y_K_f, delimiter=',', fmt='%.4f')
        np.savetxt(base_path.with_name(f"{base_path.stem}_X_KL_f_{self.Single_obs_type['First']}.csv"), self.X_KL_f, delimiter=',', fmt='%.4f')
        np.savetxt(base_path.with_name(f"{base_path.stem}_Y_KL_f_{self.Single_obs_type['First']}.csv"), self.Y_KL_f, delimiter=',', fmt='%.4f')
        if self.Another_Y_K_a is not None:
            np.savetxt(base_path.with_name(f"{base_path.stem}_Y_K_f_{self.Single_obs_type['Second']}.csv"), self.Another_Y_K_a,
                       delimiter=',', fmt='%.4f')
        if self.Another_Y_KL_a is not None:
            np.savetxt(base_path.with_name(f"{base_path.stem}_Y_KL_f_{self.Single_obs_type['Second']}.csv"), self.Another_Y_KL_a,
                   delimiter=',', fmt='%.4f')
    def run(self):
        scaled_sd = self.obs_sd * np.sqrt(self.N_iter)
        for out_iter in range(1, self.N_iter + 1):
            logging.info('<'*20 + f'External iteration {out_iter} begins.' + '>'*20)
            logging.info('<'*20 + f'ESMDA outer iteration {out_iter} begins' + '>'*20)
            X_K = ES.update(self.X_K_f,self.Y_K_f,self.obs[:self.length_of_obs['N11']],scaled_sd,self.param_range,self.length_of_obs['N11'])
            # print(X_K)
            run_esmda = MTFR(self.work_dir, self.param_range, self.N_e, self.length_of_obs, self.N_iter, X_K, out_iter)
            self.X_K_f, self.Y_K_f, self.Another_Y_K_a = run_esmda.MTFRSHAW(self.N_threads, self.obs_type,
                                                                            self.relevant_headers, self.mapping,
                                                                            show_progress=True)
            logging.info('<'*20 + f'ESMDA outer iteration {out_iter} completed' + '>'*20)
            logging.info('<'*20 + f'ILUES external iteration {out_iter} begins' + '>'*20)
            X_KL = ILUES.local_update(out_iter, self.X_KL_f, self.Y_KL_f, self.obs[:self.length_of_obs['N11']], scaled_sd,
                                       self.param_range,self.C_XX, self.C_Y, self.alpha,self.method_flag, self.beta,
                                       self.length_of_obs['N11'])
            # print(X_KL)
            run_ilues = MTFR(self.work_dir, self.param_range, self.N_e, self.length_of_obs, self.N_iter, X_KL, out_iter)
            self.X_KL_f, self.Y_KL_f,self.Another_Y_KL_a = run_ilues.MTFRSHAW(self.N_threads, self.obs_type,
                        self.relevant_headers, self.mapping, show_progress=True)
            logging.info('<'*20 + f'ILUES external iteration {out_iter} completed' + '>'*20)
            self.SaveCsv(out_iter)
        Y_K = np.concatenate((self.Y_K_f, self.Another_Y_K_a)) if self.Another_Y_K_a is not None else self.Y_K_f
        Y_KL = np.concatenate((self.Y_KL_f, self.Another_Y_KL_a)) if self.Another_Y_KL_a is not None else self.Y_KL_f
        plot.plot_results(self.obs, self.work_dir, Y_K,'ESMDA')
        plot.plot_results(self.obs, self.work_dir, Y_KL,'ILUES')
        true_P = []
        with open(Path(self.work_dir)/'Model'/'Ture Parameters.csv', 'r', encoding='gbk') as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                if not row:
                    continue
                try:
                    val = float(row[1])
                    true_P.append(val)
                except (IndexError, ValueError):
                    continue
        if true_P:
            pk = true_P
            pkl = true_P
            print('The true value of the parameter exists.')
        else:
            pk = Best_k
            pkl = Best_kl
            print('The true value of the parameter does not exist!!!!!!!!!!')
        Iterations = IterationPloter(self.N_iter, self.N_par, self.N_e, self.N_layer, self.curve_type,
                                     self.param_range, self.N_PLANT, self.Residue, self.Stewart_Jarvis, self.par_name)
        Iterations.plot_iteration_par(self.work_dir, self.obs_type,pk,Optimization='ESMDA')
        Iterations.plot_iteration_par(self.work_dir, self.obs_type,pkl,Optimization='ILUES')
        quantile = Quantile()
        quantile.plot_layered_figure(self.work_dir, self.N_iter, self.N_e, self.obs_type, self.confidence_level,
                                     Optimization='ESMDA')
        quantile.plot_layered_figure(self.work_dir, self.N_iter, self.N_e, self.obs_type, self.confidence_level,
                                     Optimization='ILUES')
        joint_distribution(self.couple, self.param_range, Path(self.ensemble_path)/f'ensemble_{self.N_iter}_X_K_f_{self.obs_type}.csv',
                           Path(self.Figout)/'Joint_distribution_k.png')
        joint_distribution(self.couple, self.param_range, Path(self.ensemble_path)/f'ensemble_{self.N_iter}_X_KL_f_{self.obs_type}.csv',
                           Path(self.Figout)/'Joint_distribution_kl.png')
        Clear.clear(self.N_threads, Path(self.work_dir)/ 'Model')
        logging.info('*'*30 + 'finish'+'*'*30 + '\n')
        logging.info(' '*20 + f'Please read the model results from {self.work_dir}' + ' '*20 + '\n')
        logging.info('*'*65+'\n')
