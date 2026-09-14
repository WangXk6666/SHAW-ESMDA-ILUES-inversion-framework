import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from scipy import stats

class Relationship_of_Pars:

    
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

        self.data = pd.read_csv(self.csv_path, header=None).values
        print(f"Data shape: {self.data.shape}")
        print(f"Number of parameters (N_pars): {self.data.shape[0]}")
        print(f"Ensemble size (N_e): {self.data.shape[1]}")
        return self.data
    
    def _draw(self):
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
            param_i = self.data[i, :]
            param_j = self.data[j, :]
            ax.scatter(param_i, param_j, alpha=0.4, s=15, c='steelblue', edgecolors='none')
            
            x_min, x_max = self.param_range[i]
            y_min, y_max = self.param_range[j]
            ax.set_xlim(x_min, x_max)
            ax.set_ylim(y_min, y_max)
            
            ax.set_xlabel(f'Parameter {i}', fontsize=10)
            ax.set_ylabel(f'Parameter {j}', fontsize=10)
            ax.set_title(f'Joint Distribution: Par{i} vs Par{j}', fontsize=11, fontweight='bold')
            ax.grid(True, alpha=0.3)
            r, p = stats.pearsonr(param_i, param_j)
            ax.text(0.05, 0.95, f'r = {r:.3f}', transform=ax.transAxes, 
                   fontsize=9, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        for idx in range(n_pairs, len(axes) if n_pairs > 1 else 1):
            axes[idx].set_visible(False)
        
        plt.tight_layout()
        return fig
    
    def _save(self, fig=None, dpi=300):
        if fig is None:
            fig = plt.gcf()
        
        out_dir = os.path.dirname(self.out_path)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir)
        
        fig.savefig(self.out_path, dpi=dpi, bbox_inches='tight')
        print(f"Image saved to:{self.out_path}")
        plt.close(fig)