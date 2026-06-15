import os
import numpy as np
from pathlib import Path
from SHAW.SHAWParRewrite import ParaRewrite
from SHAW.SHAW_exe import Shaw
from SHAWFinalResult.ReadFinal import ReadFinalResult as Reader
from SHAWFinalResult.FitResult import FitResult
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
class RunBestPar:
    def _CBP(self,estimate_par,nse, r2, rmse, choose_index, SavePath, SitPath, mapping):
        self.Best_Par = None
        if choose_index == 'rmse':
            OrderArg = np.argsort(r2)
            self.Best_Par = estimate_par[:,OrderArg[-1]]
            logging.info(f'select self.Best_Par={self.Best_Par} based on rmse')
        elif choose_index == 'r2':
            OrderArg = np.argsort(rmse)
            self.Best_Par = estimate_par[:,OrderArg[0]]
            logging.info(f'select self.Best_Par={self.Best_Par} based on r2')
        elif choose_index == 'nse':
            OrderArg = np.argsort(nse)
            self.Best_Par = estimate_par[:,OrderArg[0]]
            logging.info(f'select self.Best_Par={self.Best_Par} based on nse')
        else:
            raise ValueError(f'please check  choose_index')
        np.savetxt(SavePath,self.Best_Par,delimiter=",",fmt="%.4f")
        ParaRewrite.rewrite(SitPath, self.Best_Par, mapping)
        return self.Best_Par
    def BestPar(self, estimate_par, nse, r2, rmse, choose_index, work_dir, obs_type, thread_id, optimization, mapping):
        Element ={
        'SitPath': os.path.join(work_dir, "Model", "SIT.INP"),
        'SavePath': os.path.join(work_dir, f"Ensemble/BestPar{optimization}.csv"),
        'EXEPATH': os.path.join(work_dir, "Model","SHAW303"),
        'Obs_path_moi': os.path.join(work_dir, "Model","Obs_liquid.csv"),
        'Obs_path_temp': os.path.join(work_dir, "Model","Obs_temperature.csv"),
        'Obs_path_mat': os.path.join(work_dir, "Model","Obs_matric.csv"),
        'Obs_path_et': os.path.join(work_dir,"Model", "Obs_evapotranspiration.csv"),
        'Obs_path_solute': os.path.join(work_dir,"Model", "Obs_solute.csv"),
        'Obs_path_total_salt': os.path.join(work_dir,"Model", "Obs_total_salt.csv"),
        'Sim_path_moi': os.path.join(work_dir, "Model",'LIQUID.OUT'),
        'Sim_path_temp': os.path.join(work_dir, "Model",'TEMPERATURE.OUT'),
        'Sim_path_mat': os.path.join(work_dir,"Model", 'MATRIC.OUT'),
        'Sim_path_et': os.path.join(work_dir, "Model", 'SUMMARY WATER BALANCE.OUT'),
        'Sim_path_solute': os.path.join(work_dir, "Model",'SOLUTE CONCENTRATION.OUT'),
        'Sim_path_total_salt': os.path.join(work_dir, "Model",'TOTAL SALT CONCENTRATION.OUT'),
        'ylim_moi': [0, 0.5],
        'ylim_temp': [-30, 30],
        'ylim_mat':[-10000, 0],
        'ylim_et': [0, 10],
        'ylim_solute': None,
        'ylim_total_salt': None,
        'ytitle_moi': 'Liquid Volumetric Water Content (m³/m³)',
        'ytitle_temp': 'Soil temperature (℃)',
        'ytitle_mat': 'Matric potential (m)',
        'ytitle_et': 'ET (mm)',
        'ytitle_solute': 'Solute concentration (mol/L)',
        'ytitle_total_salt': 'Total salt concentration (mol/L)',
        }
        if obs_type == 'temp':
            Best_Pars = self._CBP(estimate_par, nse, r2, rmse, choose_index, Element['SavePath'], Element['SitPath'], mapping)
            Shaw.execute(thread_id, Element['EXEPATH'], Path(work_dir)/'Model')
            Read = Reader()
            Data_1 = Read.ReadData(Element['Obs_path_temp'], Element['Sim_path_temp'], 'temp')
            Fit_sim_obs = FitResult()
            Fit_sim_obs.Fit(Data_1, work_dir,'temp',optimization,
                            Element['ytitle_temp'], Element['ylim_temp'])
            Data_2 = Read.ReadData(Element['Obs_path_moi'], Element['Sim_path_moi'],'moi')
            Fit_sim_obs = FitResult()
            Fit_sim_obs.Fit(Data_2 ,work_dir, 'moi',optimization,
                            Element['ytitle_moi'], Element['ylim_moi'])
        elif obs_type == 'moi':
            Best_Pars = self._CBP(estimate_par, nse, r2, rmse, choose_index, Element['SavePath'], Element['SitPath'], mapping)
            Shaw.execute(thread_id, Element['EXEPATH'], Path(work_dir)/'Model')
            Read = Reader()
            Data_1 = Read.ReadData(Element['Obs_path_temp'], Element['Sim_path_temp'],'temp')
            Fit_sim_obs = FitResult()
            Fit_sim_obs.Fit(Data_1, work_dir, 'temp', optimization,
                            Element['ytitle_temp'], Element['ylim_temp'])
            Data_2 = Read.ReadData(Element['Obs_path_moi'], Element['Sim_path_moi'],'moi')
            Fit_sim_obs = FitResult()
            Fit_sim_obs.Fit(Data_2, work_dir, 'moi', optimization,
                            Element['ytitle_moi'], Element['ylim_moi'])
        elif obs_type == 'mat':
            Best_Pars = self._CBP(estimate_par, nse, r2, rmse, choose_index, Element['SavePath'], Element['SitPath'], mapping)
            Shaw.execute(thread_id, Element['EXEPATH'], Path(work_dir)/'Model')
            Read = Reader()
            Data_1 = Read.ReadData(Element['Obs_path_temp'], Element['Sim_path_temp'], 'temp')
            Fit_sim_obs = FitResult()
            Fit_sim_obs.Fit(Data_1, work_dir, 'temp', optimization,
                            Element['ytitle_temp'], Element['ylim_temp'])
            Data_2 = Read.ReadData(Element['Obs_path_mat'], Element['Sim_path_mat'],'mat')
            Fit_sim_obs = FitResult()
            Fit_sim_obs.Fit(Data_2, work_dir, 'mat', optimization,
                            Element['ytitle_mat'], Element['ylim_mat'])
        elif obs_type == 'solute':
            Best_Pars = self._CBP(estimate_par, nse, r2, rmse, choose_index, Element['SavePath'], Element['SitPath'], mapping)
            Shaw.execute(thread_id, Element['EXEPATH'], Path(work_dir)/'Model')
            Read = Reader()
            Data_1 = Read.ReadData(Element['Obs_path_solute'], Element['Sim_path_solute'], 'solute')
            Fit_sim_obs = FitResult()
            Fit_sim_obs.Fit(Data_1, work_dir, 'solute', optimization,
                            Element['ytitle_solute'], Element['ylim_solute'])
            Data_2 = Read.ReadData(Element['Obs_path_moi'], Element['Sim_path_moi'],'moi')
            Fit_sim_obs = FitResult()
            Fit_sim_obs.Fit(Data_2, work_dir, 'moi', optimization,
                            Element['ytitle_moi'], Element['ylim_moi'])
        elif obs_type == 'total_salt':
            Best_Pars = self._CBP(estimate_par, nse, r2, rmse, choose_index, Element['SavePath'], Element['SitPath'], mapping)
            Shaw.execute(thread_id, Element['EXEPATH'], Path(work_dir)/'Model')
            Read = Reader()
            Data_1 = Read.ReadData(Element['Obs_path_total_salt'], Element['Sim_path_total_salt'], 'total_salt')
            Fit_sim_obs = FitResult()
            Fit_sim_obs.Fit(Data_1, work_dir, 'total_salt', optimization,
                            Element['ytitle_total_salt'], Element['ylim_total_salt'])
            Data_2= Read.ReadData(Element['Obs_path_moi'], Element['Sim_path_moi'],'moi')
            Fit_sim_obs = FitResult()
            Fit_sim_obs.Fit(Data_2, work_dir, 'moi', optimization,
                            Element['ytitle_moi'], Element['ylim_moi'])
        elif obs_type == 'ET':
            Best_Pars = self._CBP(estimate_par, nse, r2, rmse, choose_index, Element['SavePath'], Element['SitPath'], mapping)
            Shaw.execute(thread_id, Element['EXEPATH'], Path(work_dir)/'Model')
            Read = Reader()
            Data_1 = Read.ReadData(Element['Obs_path_et'], Element['Sim_path_et'], 'ET')
            Fit_sim_obs = FitResult()
            Fit_sim_obs.Fit(Data_1, work_dir, 'ET', optimization,
                            Element['ytitle_et'], Element['ylim_et'])
            Data_2= Read.ReadData(Element['Obs_path_moi'], Element['Sim_path_moi'],'moi')
            Fit_sim_obs = FitResult()
            Fit_sim_obs.Fit(Data_2, work_dir, 'moi', optimization,
                            Element['ytitle_moi'], Element['ylim_moi'])
        else:
            raise ValueError(f'obs_type must be ([moi, temp, mat, ET, solute, total_salt')
        return Best_Pars






