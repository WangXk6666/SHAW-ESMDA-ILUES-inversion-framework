import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, DayLocator, MonthLocator
from datetime import datetime
from SHAWFinalResult.ReadFinal import ReadFinalResult
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
class Quantile:
    def __init__(self):
        self.sim_data = None
        self.another_sim_data = None
        self.font_config = {'family': 'Times New Roman', 'size': 18}
        plt.rcParams['font.family'] = self.font_config['family']
        plt.rcParams['font.size'] = self.font_config['size']
    def _read_sim_data(self, Iter_sim_path, N_e):
        sim_data = pd.read_csv(Iter_sim_path, header=None, usecols=range(N_e)).values
        logging.info(f'sim_data = {sim_data}')
        return sim_data
    def _reshape_sim_data(self, sim_data, n_nodes, n_time_steps):
        total_elements = n_nodes * n_time_steps
        if sim_data.shape[0] < total_elements:
            raise ValueError(f"模拟数据行数 {sim_data.shape[0]} 小于所需元素数 {total_elements}")
        return sim_data[:total_elements, :].reshape(n_nodes, n_time_steps, -1)
    def _parse_single_format_date(self, date_array):
        if isinstance(date_array, np.ndarray) and str(date_array.dtype).startswith('datetime64'):
            return date_array.astype('datetime64[ns]')
        date_formats = [
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M",
            "%Y/%m/%d %H:%M",
            "%Y-%m-%d %H:%M",
            "%Y/%m/%d",
            "%Y-%m-%d"]
        test_date = None
        for d in date_array:
            if pd.notna(d) and str(d).strip():
                test_date = str(d).strip()
                break
        if not test_date:
            raise ValueError("时间数组中无有效时间数据")
        target_fmt = None
        for fmt in date_formats:
            try:
                datetime.strptime(test_date, fmt)
                target_fmt = fmt
                break
            except ValueError:
                continue
        if not target_fmt:
            raise ValueError(
                f"时间格式不支持！当前测试格式：{test_date}\n"
                f"支持格式包括：2021-09-30T00:00:00、2021-09-30T00:00、2025/1/1 00:00、2025-1-1 00:00、2025/1/1、2025-1-1"
            )
        parsed_dates = []
        for d in date_array:
            if pd.notna(d) and str(d).strip():
                parsed_dates.append(datetime.strptime(str(d).strip(), target_fmt))
            else:
                parsed_dates.append(pd.NaT)
        return np.array(parsed_dates, dtype='datetime64[ns]')
    def _get_date_locator(self, min_date, max_date):
        delta = max_date - min_date
        total_days = delta.astype('timedelta64[D]').astype(int)
        if total_days >= 90:
            return MonthLocator(bymonthday=1)
        else:
            if total_days <= 14:
                return DayLocator(interval=2)
            elif total_days <= 30:
                return DayLocator(interval=5)
            else:
                return DayLocator(interval=10)
    def _save_combined_data(self, dates, nodes_name_list, sim_lower, sim_mean, sim_upper, obs_type, base_work_dir, Optimization):
        date_strings = []
        for date in dates:
            if pd.isna(date):
                date_strings.append('')
            else:
                date_strings.append(pd.to_datetime(date).strftime("%Y/%m/%d %H:%M"))
        data = {'Date': date_strings}
        for i, node_name in enumerate(nodes_name_list):
            clean_name = node_name.replace(' ', ' ')
            data[f'{clean_name}_lower'] = sim_lower[i]
            data[f'{clean_name}_mean'] = sim_mean[i]
            data[f'{clean_name}_upper'] = sim_upper[i]
        df = pd.DataFrame(data)
        save_path = Path(base_work_dir)/f'Ensemble'/f'Quantile_{obs_type}.csv'
        df.to_csv(save_path, index=False, float_format='%.6f')
        logging.info(f"合并数据已保存至：{save_path}")

    def _plot_subfigures(self, nodes_range, nodes_name_list, sim_mean, sim_lower, sim_upper,
                         parsed_date, observed_data, y_label, y_lim, save_path):
        start_idx, end_idx = nodes_range
        num_nodes = end_idx - start_idx
        rows = (num_nodes + 2) // 3
        fig, axes = plt.subplots(rows, 3, figsize=(18, 5 * rows))
        axes = axes.flatten()
        date_formatter = DateFormatter('%m/%d')
        global_min_date = parsed_date.min()
        global_max_date = parsed_date.max()
        locator = self._get_date_locator(global_min_date, global_max_date)
        for i in range(start_idx, end_idx):
            ax_idx = i - start_idx
            obs_i = observed_data[:, i]
            sim_mean_i = sim_mean[i]
            sim_lower_i = sim_lower[i]
            sim_upper_i = sim_upper[i]
            ax = axes[ax_idx]
            ax.fill_between(
                parsed_date, sim_lower_i, sim_upper_i,
                color='lightblue', alpha=0.8,
                label=f'{int(self.confidence_level * 100)}% Posterior Spread'
            )
            ax.plot(
                parsed_date, sim_mean_i,
                color='blue', linewidth=1.5,
                label='Simulated Value'
            )
            ax.scatter(
                parsed_date, obs_i,
                color='white', edgecolors='red',
                s=25, linewidth=1,
                label='Observed Value'
            )
            ax.set_xlim(global_min_date, global_max_date)
            ax.grid(False)
            ax.legend(loc='best', frameon=False, prop=self.font_config)
            ax.set_title(f'Node: {nodes_name_list[i]}', fontweight='bold', **self.font_config)
            ax.set_xlabel('Date',** self.font_config)
            ax.set_ylabel(y_label, **self.font_config)
            if y_lim is not None:
                ax.set_ylim(y_lim)
            ax.tick_params(axis='both', which='major', labelsize=self.font_config['size'])
            for label in ax.get_yticklabels():
                label.set_fontproperties(self.font_config['family'])
            ax.xaxis.set_major_locator(locator)
            ax.xaxis.set_major_formatter(date_formatter)
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=0, ha='center',** self.font_config)
        for j in range(num_nodes, len(axes)):
            axes[j].set_visible(False)
        plt.tight_layout(pad=1.0)
        plt.savefig(save_path, dpi=300, bbox_inches='tight', pad_inches=0.1)
        plt.close()
        logging.info(f"图片已保存至：{save_path}")
    def plot_layered_figure(self, base_work_dir, N_iter, N_e, obs_type,
                            confidence_level=0.9, Optimization='ILUES'):
        logging.info(f'====================================Quantile begains to graph========================================')
        self.confidence_level = confidence_level
        reader = ReadFinalResult()
        Element = {'Obs_temp_path': os.path.join(base_work_dir,'Model', 'Obs_temperature.csv'),
                   'Obs_moi_path': os.path.join(base_work_dir, 'Model','Obs_liquid.csv'),
                   'Obs_mat_path': os.path.join(base_work_dir, 'Model','Obs_matric.csv'),
                   'Obs_et_path': os.path.join(base_work_dir, 'Model','Obs_evapotranspiration.csv'),
                   'Obs_solute_path': os.path.join(base_work_dir, 'Model','Obs_solute.csv'),
                   'Obs_total_salt_path': os.path.join(base_work_dir,'Model', 'Obs_total_salt.csv'),
                   'Sim_temp_path': os.path.join(base_work_dir, 'Model','TEMPERATURE.OUT'),
                   'Sim_moi_path': os.path.join(base_work_dir, 'Model','LIQUID.OUT'),
                   'Sim_mat_path': os.path.join(base_work_dir,'Model', 'MATRIC.OUT'),
                   'Sim_et_path': os.path.join(base_work_dir,'Model', 'SUMMARY WATER BALANCE.OUT'),
                   'Sim_solute_path': os.path.join(base_work_dir, 'Model','SOLUTE CONCENTRATION.OUT'),
                   'Sim_total_salt_path': os.path.join(base_work_dir,'Model', 'TOTAL SALT CONCENTRATION.OUT'),
                   'ylim_temp': [-30, 30], 'ylim_moi': [0, 0.5], 'ylim_mat': [0, -10000], 'ylim_et': [0, 5],
                   'ylim_solute':None, 'ylim_total_salt':None,
                   'ytitle_temp': 'Temperature (℃)', 'ytitle_moi': 'Liquid Volumetric Water Content (m³/m³)',
                   'ytitle_mat': 'Matric Potential (m)', 'ytitle_et': 'ET (mm)','ytitle_solute':'Solute Concentration (mol/L)',
                   'ytitle_total_salt':'Total Salt Concentration (mol/L)'}
        if obs_type == 'temp':
            one_obs_type = 'temp'
            Obs_path = Element['Obs_temp_path']
            Sim_path = Element['Sim_temp_path']
            Another_obs_path = Element['Obs_moi_path']
            Another_sim_path = Element['Sim_moi_path']
            Another_obs_type = 'moi'
            ylim = Element['ylim_temp']
            Another_ylim = Element['ylim_moi']
            y_label = Element['ytitle_temp']
            Another_y_label = Element['ytitle_moi']
            _, _, _, date_data, observed_data, ObsHeaders_temp = reader.ReadData(Another_obs_path, Sim_path,
                                                                                 Another_obs_type)

        elif obs_type == 'moi':
            one_obs_type = 'moi'
            Obs_path = Element['Obs_moi_path']
            Sim_path = Element['Sim_moi_path']
            Another_obs_path = Element['Obs_temp_path']
            Another_sim_path = Element['Sim_temp_path']
            Another_obs_type = 'temp'
            ylim = Element['ylim_moi']
            Another_ylim = Element['ylim_temp']
            y_label = Element['ytitle_moi']
            Another_y_label = Element['ytitle_temp']
            _, _, _, Another_date_data, Another_observed_data, ObsHeaders_temp = reader.ReadData(Another_obs_path,
                                                                                                 Sim_path,
                                                                                                 Another_obs_type)

        elif obs_type == 'mat':
            one_obs_type = 'mat'
            Obs_path = Element['Obs_mat_path']
            Sim_path = Element['Sim_mat_path']
            Another_obs_path = Element['Obs_temp_path']
            Another_sim_path = Element['Sim_temp_path']
            Another_obs_type = 'temp'
            ylim = Element['ylim_mat']
            Another_ylim = Element['ylim_temp']
            y_label = Element['ytitle_mat']
            Another_y_label = Element['ytitle_mat']
            _, _, _, Another_date_data, Another_observed_data, ObsHeaders_temp = reader.ReadData(Another_obs_path,
                                                                                                 Sim_path,
                                                                                                 Another_obs_type)

        elif obs_type == 'solute':
            one_obs_type = 'solute'
            Obs_path = Element['Obs_solute_path']
            Sim_path = Element['Sim_solute_path']
            Another_obs_path = Element['Obs_moi_path']
            Another_sim_path = Element['Sim_moi_path']
            Another_obs_type = 'moi'
            ylim = Element['ylim_solute']
            Another_ylim = Element['ylim_moi']
            y_label = Element['ytitle_solute']
            Another_y_label = Element['ytitle_moi']
            _, _, _, Another_date_data, Another_observed_data, ObsHeaders_temp = reader.ReadData(Another_obs_path,
                                                                                                 Sim_path,
                                                                                                 Another_obs_type)

        elif obs_type == 'total_salt':
            # 基质势类型（唯一类型）
            one_obs_type = 'total_salt'
            Obs_path = Element['Obs_total_salt_path']
            Sim_path = Element['Sim_total_salt_path']
            Another_obs_path = Element['Obs_moi_path']
            Another_sim_path = Element['Sim_moi_path']
            Another_obs_type = 'moi'
            ylim = Element['ylim_total_salt']
            Another_ylim = Element['ylim_moi']
            y_label = Element['ytitle_total_salt']
            Another_y_label = Element['ytitle_moi']
            _, _, _, Another_date_data, Another_observed_data, ObsHeaders_temp = reader.ReadData(Another_obs_path,
                                                                                                 Sim_path,
                                                                                                 Another_obs_type)

        elif obs_type == 'ET':
            one_obs_type = 'ET'
            Obs_path = Element['Obs_et_path']
            Sim_path = Element['Sim_et_path']
            Another_obs_path = Element['Obs_moi_path']
            Another_sim_path = Element['Sim_temp_path']
            Another_obs_type = 'moi'
            ylim = Element['ylim_et']
            Another_ylim = Element['ylim_moi']
            y_label = Element['ytitle_et']
            Another_y_label = Element['ytitle_moi']
            _, _, _, Another_date_data, Another_observed_data, ObsHeaders_temp = reader.ReadData(Another_obs_path,
                                                                                                 Sim_path,
                                                                                                 Another_obs_type)
        else:
            valid_options = ("['moi', 'temp', 'mat', 'ET', 'solute', 'total_salt']")
            raise ValueError(f"obs_type 必须为 {valid_options} 之一，当前值为 '{obs_type}'")
        if Optimization == 'ESMDA':
            name='K'
        else: name='KL'
        Iter_sim_path = Path(base_work_dir)/f"Ensemble" / f"ensemble_{N_iter}_Y_{name}_f_{one_obs_type}.csv"
        base_save_name = Path("Figures") / f"ensemble_{N_iter}_Y_{name}_f_{one_obs_type}"
        _, _, _, date_data, observed_data, ObsHeaders = reader.ReadData(Obs_path, Sim_path, one_obs_type)
        Nodes_name_list = ObsHeaders[1:]
        N_nodes = len(Nodes_name_list)
        parsed_date = self._parse_single_format_date(date_data)
        sim_data = self._read_sim_data(Iter_sim_path, N_e)
        N_nodes_obs = observed_data.shape[0]
        self.sim_data = self._reshape_sim_data(sim_data, N_nodes, N_nodes_obs)
        self._validate_data(observed_data, N_nodes_obs, parsed_date, N_nodes)
        alpha = (1 - confidence_level) / 2
        sim_mean = np.mean(self.sim_data, axis=2)
        sim_lower = np.quantile(self.sim_data, alpha, axis=2)
        sim_upper = np.quantile(self.sim_data, 1 - alpha, axis=2)
        self._save_combined_data(
                dates=parsed_date,
                nodes_name_list=Nodes_name_list,
                sim_lower=sim_lower,
                sim_mean=sim_mean,
                sim_upper=sim_upper,
                obs_type=one_obs_type,
                base_work_dir=base_work_dir,
                Optimization=Optimization)
        self._plot_subfigures((0, N_nodes), Nodes_name_list, sim_mean, sim_lower, sim_upper, parsed_date,
                                  observed_data, y_label, ylim, Path(base_work_dir) / f"{base_save_name}.png")
        _, _, _, another_date_data, another_observed_data, another_ObsHeaders = reader.ReadData(Another_obs_path,
                                                                                                    Another_sim_path,
                                                                                                    Another_obs_type)
        another_Nodes_name_list = another_ObsHeaders[1:]
        another_N_nodes = len(another_Nodes_name_list)
        another_N_nodes_obs = another_observed_data.shape[0]

        Another_Iter_sim_path = Path(base_work_dir) / "Ensemble" / f"ensemble_{N_iter}_Y_{name}_f_{Another_obs_type}.csv"
        Another_base_save_name = Path("Figures")/ f"ensemble_{N_iter}_Y_{name}_f_{Another_obs_type}"
        another_sim_data = self._read_sim_data(Another_Iter_sim_path, N_e)
        self.another_sim_data = self._reshape_sim_data(another_sim_data, another_N_nodes, another_N_nodes_obs)
        self._validate_data(another_observed_data, another_N_nodes_obs,
                                self._parse_single_format_date(another_date_data), another_N_nodes)
        another_sim_mean = np.mean(self.another_sim_data, axis=2)
        another_sim_lower = np.quantile(self.another_sim_data, alpha, axis=2)
        another_sim_upper = np.quantile(self.another_sim_data, 1 - alpha, axis=2)
        self._save_combined_data(
                dates=self._parse_single_format_date(another_date_data),
                nodes_name_list=another_Nodes_name_list,
                sim_lower=another_sim_lower,
                sim_mean=another_sim_mean,
                sim_upper=another_sim_upper,
                obs_type=Another_obs_type,
                base_work_dir=base_work_dir,
                Optimization=Optimization
            )
        self._plot_subfigures((0, another_N_nodes), another_Nodes_name_list, another_sim_mean,
                                  another_sim_lower, another_sim_upper,
                                  self._parse_single_format_date(another_date_data),
                                  another_observed_data, Another_y_label, Another_ylim,
                                  Path(base_work_dir) / f'{Another_base_save_name}.png')

        logging.info(f'====================================Quantile finishes graphing========================================')

    def _validate_data(self, observed_data, N_nodes_obs, parsed_date, N_nodes):
        if len(observed_data.shape) != 2:
            raise ValueError(
                f"观测数据必须为二维数组（时间步数×节点数），当前为{len(observed_data.shape)}维"
            )
        if observed_data.shape[0] != N_nodes_obs or len(parsed_date) != N_nodes_obs:
            raise ValueError(
                f"时间步数不匹配：\n"
                f"观测数据行数（时间步数）={observed_data.shape[0]}\n"
                f"模拟数据每个节点时间步数={N_nodes_obs}\n"
                f"日期数据长度={len(parsed_date)}"
            )
        if observed_data.shape[1] != N_nodes:
            raise ValueError(
                f"节点数不匹配：\n"
                f"观测数据列数（节点数）={observed_data.shape[1]}\n"
                f"观测点名称数量={N_nodes}"
            )
