import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.ticker import MaxNLocator, MultipleLocator
import matplotlib as mpl
from matplotlib import rcParams
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
class PlotResult:
    @staticmethod
    def plot_results(obs, work_dir, Y_KL_f,Optimization):
        name={"ILUES":"kl","ESMDA":"k"}
        rcParams['font.family'] = 'Times New Roman'
        rcParams['font.weight'] = 'normal'
        rcParams['font.size'] = 10
        N_obs = Y_KL_f.shape[0]
        N_e = Y_KL_f.shape[1]
        obs_flat = obs.flatten() if obs.ndim > 1 else obs.ravel()
        assert obs_flat.shape == (N_obs,), f"观测数据形状错误，应为({N_obs},)，实际为{obs_flat.shape}"
        rmse_kl = np.zeros(N_e)
        r2_kl = np.zeros(N_e)
        nse_kl = np.zeros(N_e)
        for member_idx in range(N_e):
            y_kl_member = Y_KL_f[:, member_idx]
            diff_kl = y_kl_member - obs_flat
            rmse_kl[member_idx] = np.sqrt(np.nanmean(diff_kl ** 2))
            ss_res_kl = np.nansum(diff_kl ** 2)
            ss_tot_kl = np.nansum((obs_flat - np.nanmean(obs_flat)) ** 2)
            nse_kl[member_idx] = 1 - (ss_res_kl / ss_tot_kl) if ss_tot_kl != 0 else 0
            corr_coef_kl= np.corrcoef(obs_flat, y_kl_member)[0, 1]
            if len(obs_flat) > 1 and np.std(obs_flat) != 0 and np.std(y_kl_member) != 0:
                r2_kl[member_idx] = corr_coef_kl ** 2
            else:
                r2_kl[member_idx] = 0
        rmse_data = {'member_index': np.arange(1, N_e + 1),f'rmse_{name[Optimization]}': rmse_kl,
                     f'r2_{name[Optimization]}': r2_kl,f'nse_{name[Optimization]}': nse_kl}
        df_rmse = pd.DataFrame(rmse_data)
        work_dir_path = Path(work_dir)
        csv_save_path = work_dir_path / "Ensemble"/f"rmse_r2_nse_comparison_{name[Optimization]}.csv"
        df_rmse.to_csv(csv_save_path, index=False, encoding='utf-8-sig')
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        plt.subplots_adjust(wspace=0.3)
        ax1, ax2, ax3 = axes[0], axes[1], axes[2]
        members = np.arange(1, N_e + 1)
        mean_rmse_kl = np.nanmean(rmse_kl)
        mean_r2_kl = np.nanmean(r2_kl)
        mean_nse_kl = np.nanmean(nse_kl)
        for ax in [ax1, ax2, ax3]:
            ax.set_xlim(0, N_e)
            if N_e > 20:
                tick_positions = np.linspace(0, N_e, 5)
                ax.set_xticks(tick_positions)
            else:
                tick_positions = np.arange(0, N_e + 1, 1)
                ax.set_xticks(tick_positions)
        line2, = ax1.plot(members, rmse_kl, 'o-', linewidth=2, color='green',
                          markersize=8, markeredgecolor='green', markerfacecolor='white',
                          markeredgewidth=2, label=Optimization)
        mean_line2 = ax1.axhline(mean_rmse_kl, color='blue', linestyle='--', linewidth=2, alpha=0.7, label=f'{Optimization} mean')
        ax1.set_xlabel('N_e', fontweight='bold')
        ax1.set_ylabel('RMSE', fontweight='bold')
        ax1.set_title('RMSE\n'f'Mean_{Optimization}:{mean_rmse_kl:.4f}', fontweight='bold')
        ax1.legend(loc='best', frameon=True, ncol=2)
        ax1.grid(True, linestyle='--', alpha=0.6)
        line4, = ax2.plot(members, r2_kl, 'o-', linewidth=2, color='green',
                          markersize=8, markeredgecolor='green', markerfacecolor='white',
                          markeredgewidth=2, label=Optimization)
        mean_line4 = ax2.axhline(mean_r2_kl, color='blue', linestyle='--', linewidth=2, alpha=0.7, label=f'{Optimization} mean')
        ax2.set_xlabel('N_e', fontweight='bold')
        ax2.set_ylabel('R²', fontweight='bold')
        ax2.set_title('R²\n'f'Mean_{Optimization}:{mean_r2_kl:.4f}', fontweight='bold')
        ax2.legend([line4, mean_line4], [Optimization, f'{Optimization} mean'], loc='best', frameon=True, ncol=2)
        ax2.grid(True, linestyle='--', alpha=0.6)
        line6, = ax3.plot(members, nse_kl, 'o-', linewidth=2, color='green',
                          markersize=8, markeredgecolor='green', markerfacecolor='white',
                          markeredgewidth=2, label=Optimization)
        mean_line6 = ax3.axhline(mean_nse_kl, color='blue', linestyle='--', linewidth=2, alpha=0.7, label=f'{Optimization} mean')
        ax3.set_xlabel('N_e', fontweight='bold')
        ax3.set_ylabel('NSE', fontweight='bold')
        ax3.set_title('NSE\n'f'Mean_{Optimization}:{mean_nse_kl:.4f}', fontweight='bold')
        ax3.legend([line6, mean_line6], [Optimization, f'{Optimization} mean'], loc='best', frameon=True, ncol=2)
        ax3.grid(True, linestyle='--', alpha=0.6)
        for ax in [ax1, ax2, ax3]:
            ax.tick_params(axis='both', which='major', labelsize=9)
        plt.tight_layout()
        plt.savefig(work_dir_path / 'Figures' / f'combined_results_{name[Optimization]}.png', dpi=1200, bbox_inches='tight')
        plt.close(fig)
        return rmse_kl, r2_kl, nse_kl