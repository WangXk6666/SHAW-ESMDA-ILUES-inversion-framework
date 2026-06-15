import numpy as np
from datetime import datetime, timedelta
from pyecharts import options as opts
from pyecharts.charts import Line, Page
from pyecharts.commons.utils import JsCode
import matplotlib.pyplot as plt
import matplotlib
import warnings
from matplotlib.ticker import FormatStrFormatter
import re
from pathlib import Path
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
class FitResult:
    def __init__(self):
        self.rmse_r2 = {}
        self.obs = None
        self.sim = None
        self.common_times = None
        self.common_depths = []
        self.ordered_common_depths = []
        self.obs_headers = None
        self.sim_headers = None
        self.obs_matched = None
        self.sim_matched = None
        self.obs_type = None
    def _extract_depth_number(self, depth_str):
        match = re.search(r'(\d+\.?\d*)\s*cm', depth_str, re.IGNORECASE)
        if not match:
            match = re.search(r'(\d+\.?\d*)', depth_str)
        if match:
            return float(match.group(1))
        return float('inf')
    def Fit(self, data_tuple, work_dir, obs_type, optimization, y_title, ylim=None):
        SimTimes_array, SimData_array, SimHeaders, \
            ObsTimes_array, ObsData_array, ObsHeaders = data_tuple
        self.obs = (ObsTimes_array, ObsData_array, ObsHeaders)
        self.sim = (SimTimes_array, SimData_array, SimHeaders)
        self.obs_headers = ObsHeaders
        self.sim_headers = SimHeaders
        self.obs_type = obs_type
        self._calculate_rmse_r2()
        self._plot_html(work_dir, obs_type, y_title, optimization)
        self._plot_png(work_dir, obs_type, optimization, y_title, ylim)
    def _calculate_rmse_r2(self):
        try:
            obs_times, obs_data, obs_headers = self.obs
            sim_times, sim_data, sim_headers = self.sim
            obs_times = [t.astype(datetime) for t in obs_times]
            sim_times = [t.astype(datetime) for t in sim_times]
            time_diff = np.abs(np.array(obs_times)[:, None] - np.array(sim_times))
            matched_indices = np.where(time_diff <= timedelta(hours=1))[1]
            valid_obs_indices = np.where(~np.isnan(matched_indices))[0]
            if len(valid_obs_indices) == 0:
                raise ValueError("No matching time point, please check if the data time range overlaps")
            self.common_times = [obs_times[i] for i in valid_obs_indices]
            self.obs_matched = obs_data[valid_obs_indices]
            self.sim_matched = sim_data[matched_indices[valid_obs_indices]]
            obs_params = [h for h in obs_headers if h != '时间']
            sim_params = [h for h in sim_headers if h != '时间']
            if self.obs_type in ['temp', 'moi', 'mat','solute', 'total_salt']:
                self.common_depths = list(set(obs_params) & set(sim_params))
                self.ordered_common_depths = sorted(
                    self.common_depths,
                    key=self._extract_depth_number
                )
            elif self.obs_type in ['PRECIP', 'SNOWMELT', 'INTRCP', 'ET', 'TRANSP',
                                   'CANOPY', 'SNOW', 'RESIDUE', 'SOIL']:
                matched_param = next((p for p in obs_params if p == self.obs_type), None)
                if matched_param and matched_param in sim_params:
                    self.common_depths = [matched_param]
                    self.ordered_common_depths = [matched_param]
                    logging.info(f"Find matching parameters: {matched_param}")
                else:
                    logging.info(f"Warning: No parameters matching '{self. obs_type}'"
                          f" were found in the observed or simulated data")
                    self.common_depths = []
                    self.ordered_common_depths = []
            else:
                warnings.warn(f"Unknown observation type: {self. obs_type},"
                              f" using default matching method")
                self.common_depths = list(set(obs_params) & set(sim_params))
                self.ordered_common_depths = sorted(
                    self.common_depths,
                    key=self._extract_depth_number
                )
            if not self.ordered_common_depths:
                warnings.warn("No valid parameter data (observation and"
                              " simulation parameters do not match)")
                return
            for param in self.ordered_common_depths:
                obs_param_idx = obs_headers.index(param) - 1
                sim_param_idx = sim_headers.index(param) - 1
                if self.obs_matched.ndim == 1:
                    obs_vals = self.obs_matched.astype(float)
                else:
                    obs_vals = self.obs_matched[:, obs_param_idx].astype(float)
                if self.sim_matched.ndim == 1:
                    sim_vals = self.sim_matched.astype(float)
                else:
                    sim_vals = self.sim_matched[:, sim_param_idx].astype(float)
                rmse = np.sqrt(np.nanmean((obs_vals - sim_vals) ** 2))
                ss_res = np.nansum((obs_vals - sim_vals) ** 2)
                ss_tot = np.nansum((obs_vals - np.nanmean(obs_vals)) ** 2)
                if ss_tot == 0:
                    nse = 0
                else:
                    nse = 1 - (ss_res / ss_tot)
                if len(obs_vals) > 1 and np.std(obs_vals) != 0 and np.std(sim_vals) != 0:
                    r = np.corrcoef(obs_vals, sim_vals)[0, 1]
                    r2 = r ** 2 if not np.isnan(r) else 0.0
                else:
                    r2 = 0.0
                self.rmse_r2[param] = {'RMSE': round(rmse, 4), 'NSE': round(nse, 4), 'R2': round(r2, 4)}
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"Error occurred while calculating RMSE/R ²: {str(e)}")
    def _plot_html(self, work_dir, obs_type, y_title, optimization):
        if not self.ordered_common_depths:
            warnings.warn("No valid parameter data, unable to generate HTML chart")
            return
        try:
            page = Page(page_title="Model validation results", layout=Page.SimplePageLayout)
            time_delta = (self.common_times[-1] - self.common_times[0]).total_seconds()
            date_format = "%m/%d" if time_delta > 86400 else "%m/%d %H:%M"
            for param in self.ordered_common_depths:
                obs_idx = self.obs_headers.index(param) - 1
                sim_idx = self.sim_headers.index(param) - 1
                if self.obs_matched.ndim == 1:
                    y_obs = self.obs_matched.astype(float).tolist()
                else:
                    y_obs = self.obs_matched[:, obs_idx].astype(float).tolist()
                if self.sim_matched.ndim == 1:
                    y_sim = self.sim_matched.astype(float).tolist()
                else:
                    y_sim = self.sim_matched[:, sim_idx].astype(float).tolist()
                min_length = min(len(y_obs), len(y_sim), len(self.common_times))
                y_obs = y_obs[:min_length]
                y_sim = y_sim[:min_length]
                x_data = [t.strftime(date_format) for t in self.common_times[:min_length]]
                line = (
                    Line(init_opts=opts.InitOpts(width="1000px", height="450px"))
                    .add_xaxis(x_data)
                    .add_yaxis(
                        "Observed", y_obs,
                        linestyle_opts=opts.LineStyleOpts(width=2, color="#1f77b4"),
                        symbol="circle", symbol_size=6
                    )
                    .add_yaxis(
                        "Simulated", y_sim,
                        linestyle_opts=opts.LineStyleOpts(width=2, color="#ff7f0e"),
                        symbol="diamond", symbol_size=8
                    )
                    .set_global_opts(
                        title_opts=opts.TitleOpts(
                            title=f"{param}", pos_left="center", pos_top="2%",
                            title_textstyle_opts=opts.TextStyleOpts(font_family="Times New Roman", font_size=18,
                                                                    font_weight="bold")
                        ),
                        xaxis_opts=opts.AxisOpts(
                            name="Date", name_location="center", name_gap=50,
                            axislabel_opts=opts.LabelOpts(font_family="Times New Roman", font_weight="bold")
                        ),
                        yaxis_opts=opts.AxisOpts(
                            name=y_title, name_location="center", name_gap=40,
                            splitline_opts=opts.SplitLineOpts(is_show=True),
                            axislabel_opts=opts.LabelOpts(formatter=JsCode("function(v){return v.toFixed(2);}"),
                                                          font_family="Times New Roman", font_weight="bold")
                        ),
                        tooltip_opts=opts.TooltipOpts(trigger="axis"),
                        legend_opts=opts.LegendOpts(pos_top="12%", pos_left="center"),
                        toolbox_opts=opts.ToolboxOpts(
                            is_show=True, pos_top="5%", pos_right="5%",
                            feature={"dataZoom": {"yAxisIndex": "none"}, "restore": {}, "saveAsImage": {}}
                        ),
                        datazoom_opts=[
                            opts.DataZoomOpts(type_="slider", xaxis_index=[0], range_start=0, range_end=100,
                                              pos_bottom="15%"),
                            opts.DataZoomOpts(type_="inside", xaxis_index=[0])
                        ]
                    )
                )
                text = (
                    Line()
                    .add_xaxis([x_data[-1] if x_data else ""])
                    .add_yaxis(
                        "", [y_obs[-1] if y_obs else 0], symbol_size=0,
                        label_opts=opts.LabelOpts(
                            formatter=JsCode(
                                f"function(p){{return 'RMSE: {self.rmse_r2[param]['RMSE']:.4f}\\nR²: {self.rmse_r2[param]['R2']:.4f}"
                                f"\\nNSE: {self.rmse_r2[param]['NSE']:.4f}';}}"
                            ),
                            position="right", font_size=18, font_weight="bold",
                            font_family="Times New Roman",
                            background_color="rgba(255,255,255,0.7)"
                        )
                    )
                )
                page.add(line.overlap(text))
            html_path = Path(work_dir) / "Figures"/ f"model_validation-{optimization}-{obs_type}.html"
            page.render(str(html_path))
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"HTML chart generation failed: {str(e)}")
    def _plot_png(self, work_dir, obs_type, optimization, y_title, ylim=None):
        if not self.ordered_common_depths:
            warnings.warn("No valid parameter data, unable to generate PNG chart")
            return
        try:
            plt.rcParams['font.family'] = 'Times New Roman'
            plt.rcParams['axes.unicode_minus'] = False
            plt.rcParams['figure.dpi'] = 300
            plt.rcParams['font.size'] = 11
            plt.rcParams['axes.titlesize'] = 13
            plt.rcParams['axes.labelweight'] = 'bold'
            plt.rcParams['font.weight'] = 'bold'
            n_params = len(self.ordered_common_depths)
            fig_height = min(3.5 * n_params, 18)
            fig, axs = plt.subplots(n_params, 1, figsize=(10, fig_height), sharex=False)
            if n_params == 1:
                axs = [axs]
            min_time = min(self.common_times) if self.common_times else None
            max_time = max(self.common_times) if self.common_times else None
            for idx, param in enumerate(self.ordered_common_depths):
                ax = axs[idx]
                obs_idx = self.obs_headers.index(param) - 1
                sim_idx = self.sim_headers.index(param) - 1
                if self.obs_matched.ndim == 1:
                    obs_vals = self.obs_matched.astype(float)
                else:
                    obs_vals = self.obs_matched[:, obs_idx].astype(float)
                if self.sim_matched.ndim == 1:
                    sim_vals = self.sim_matched.astype(float)
                else:
                    sim_vals = self.sim_matched[:, sim_idx].astype(float)
                min_length = min(len(obs_vals), len(sim_vals), len(self.common_times))
                obs_vals = obs_vals[:min_length]
                sim_vals = sim_vals[:min_length]
                times = self.common_times[:min_length]
                ax.plot(times, obs_vals, 'b-', linewidth=1.5)
                ax.plot(times, sim_vals, 'r--', linewidth=1.5)
                if min_time and max_time:
                    ax.set_xlim(min_time, max_time)
                if ylim is not None:
                    ax.set_ylim(ylim[0], ylim[1])
                ax.set_title(f"{param}", fontsize=13, pad=12, ha='center', fontweight='bold')
                ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
                ax.set_ylabel(y_title, labelpad=10, fontweight='bold')
                ax.set_xlabel('Date', labelpad=10, fontweight='bold')
                ax.tick_params(axis='both', which='major', labelsize=11)
                for label in ax.get_xticklabels() + ax.get_yticklabels():
                    label.set_fontname('Times New Roman')
                    label.set_fontweight('bold')
                ax.text(0.75, 0.93, f"RMSE: {self.rmse_r2[param]['RMSE']:.4f}",
                        transform=ax.transAxes, fontsize=11,
                        verticalalignment='center', horizontalalignment='left',
                        fontweight='bold')
                ax.text(0.75, 0.79, f"R²: {self.rmse_r2[param]['R2']:.4f}",
                        transform=ax.transAxes, fontsize=11,
                        verticalalignment='center', horizontalalignment='left',
                        fontweight='bold')
                ax.text(0.75, 0.65, f"NSE: {self.rmse_r2[param]['NSE']:.4f}",
                        transform=ax.transAxes, fontsize=11,
                        verticalalignment='center', horizontalalignment='left',
                        fontweight='bold')
                ax.plot([0.7, 0.74], [0.51, 0.51], 'b-', linewidth=1.5, transform=ax.transAxes)
                ax.text(0.75, 0.51, 'Observed', transform=ax.transAxes, fontsize=11,
                        verticalalignment='center', horizontalalignment='left',
                        fontweight='bold')
                ax.plot([0.7, 0.74], [0.37, 0.37], 'r--', linewidth=1.5, transform=ax.transAxes)
                ax.text(0.75, 0.37, 'Simulated', transform=ax.transAxes, fontsize=11,
                        verticalalignment='center', horizontalalignment='left',
                        fontweight='bold')
            plt.tight_layout(rect=[0, 0, 1, 0.96])
            plt.subplots_adjust(top=0.94, hspace=0.5)
            out_png = Path(work_dir)
            plt.savefig(out_png / "Figures"/f"model_validation-{optimization}-{obs_type}.png",
                        dpi=300, bbox_inches='tight', pad_inches=0.1)
            logging.info(f"Successfully generated PNG files for {n_params} parameter charts")
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"PNG chart generation failed: {str(e)}")
