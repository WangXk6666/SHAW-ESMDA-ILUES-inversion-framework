import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from scipy import stats

class Relationship_of_Pars:
    """
    分析ENKF反演参数之间关系的类
    绘制参数在二维参数空间的联合分布散点图
    
    Parameters:
    -----------
    couple : list
        需要分析的参数序号列表，如[[1,2],[2,3]]
    param_range : np.ndarray
        参数范围，形状为(N_pars, 2)
    csv_path : str
        CSV文件路径
    out_path : str
        输出图片保存路径
    """
    
    def __init__(self, couple, param_range, csv_path, out_path):
        self.couple = couple
        self.param_range = np.array(param_range)
        self.csv_path = csv_path
        self.out_path = out_path
        self.data = None
        self.data = self._read_csv()
        fig = self._draw()
        self._save(fig, 300)
        
    def _read_csv(self):
        """读取CSV文件，数据形状为(N_pars, N_e)"""
        self.data = pd.read_csv(self.csv_path, header=None).values
        print(f"数据形状: {self.data.shape}")
        print(f"参数数量 (N_pars): {self.data.shape[0]}")
        print(f"Ensemble成员数 (N_e): {self.data.shape[1]}")
        return self.data
    
    def _draw(self):
        """
        绘制参数对之间的二维联合分布散点图
        每个参数对作为一个子图，展示真实的二维参数空间分布
        """
        if self.data is None:
            self._read_csv()
        
        n_pairs = len(self.couple)
        n_cols = min(3, n_pairs)
        n_rows = int(np.ceil(n_pairs / n_cols))
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(5*n_cols, 4*n_rows))
        if n_pairs == 1:
            axes = np.array([axes])
        axes = axes.flatten() if n_pairs > 1 else axes
        
        for idx, (i, j) in enumerate(self.couple):
            ax = axes[idx] if n_pairs > 1 else axes[0]
            
            # 使用原始值，不排序！这是关键修正
            param_i = self.data[i, :]
            param_j = self.data[j, :]
            
            # 绘制二维散点图（原始值的配对）
            ax.scatter(param_i, param_j, alpha=0.4, s=15, c='steelblue', edgecolors='none')
            
            x_min, x_max = self.param_range[i]
            y_min, y_max = self.param_range[j]
            ax.set_xlim(x_min, x_max)
            ax.set_ylim(y_min, y_max)
            
            ax.set_xlabel(f'Parameter {i}', fontsize=10)
            ax.set_ylabel(f'Parameter {j}', fontsize=10)
            ax.set_title(f'Joint Distribution: Par{i} vs Par{j}', fontsize=11, fontweight='bold')
            ax.grid(True, alpha=0.3)
            
            # 添加相关系数标注
            r, p = stats.pearsonr(param_i, param_j)
            ax.text(0.05, 0.95, f'r = {r:.3f}', transform=ax.transAxes, 
                   fontsize=9, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        # 隐藏多余的子图
        for idx in range(n_pairs, len(axes) if n_pairs > 1 else 1):
            axes[idx].set_visible(False)
        
        plt.tight_layout()
        return fig
    
    def _save(self, fig=None, dpi=300):
        """保存图片"""
        if fig is None:
            fig = plt.gcf()
        
        out_dir = os.path.dirname(self.out_path)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir)
        
        fig.savefig(self.out_path, dpi=dpi, bbox_inches='tight')
        print(f"图片已保存至: {self.out_path}")
        plt.close(fig)