import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import matplotlib.gridspec as gridspec
from pathlib import Path
from typing import List, Dict, Optional
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p'
)

class IterationPloter:
    def __init__(
            self,
            N_iter: int,
            N_par: int,
            N_e: int,
            N_layer: int,
            curve_flag: int,
            param_range: np.ndarray,
            N_PLANT: int,
            Residue: bool = True,
            Stewart_Jarvis: bool = True,
            par_name: List[str] = None,
            N_other_pars: int = 0
    ):

        self.N_iter = N_iter
        self.N_par = N_par
        self.N_e = N_e
        self.N_layer = N_layer
        self.N_PLANT = N_PLANT
        self.N_other_pars = N_other_pars
        self.curve_flag = curve_flag
        self.param_range = param_range
        self.Residue = Residue
        self.Stewart_Jarvis = Stewart_Jarvis

        if par_name is not None and len(par_name) != N_par:
            raise ValueError(
                f"The length of the parameter name list ({len(par_name)}) "
                f"must match the number of parameters ({N_par})!"
            )
        self.par_name = par_name if par_name else [f"Par({i + 1})" for i in range(N_par)]

        if curve_flag not in [1, 3]:
            raise ValueError(f"The SHAW model only supports curve_flag=1 or 3, currently it is {curve_flag}.")
        self.N_par_curve = 4 if curve_flag == 1 else 5
        plt.rcParams["font.family"] = "Times New Roman"
        plt.rcParams["mathtext.fontset"] = "stix"
        plt.rcParams["font.size"] = 16
        self.obs_type = None

    def _read_csv(self, work_dir: str = ".", obs_type: str = None) -> Dict[str, np.ndarray]:
        work_dir = Path(work_dir)
        csv_data = {}
        for i in range(0, self.N_iter + 1):
            filename = self._get_csv_key(i, obs_type)
            file_path = work_dir / filename
            logging.info(f"Trying to read: {file_path}")
            if not file_path.exists():
                raise FileNotFoundError(f"{file_path} does not exist!")
            try:
                data = np.loadtxt(file_path, delimiter=',', encoding='gbk')
                csv_data[filename] = data
            except Exception as e:
                raise RuntimeError(f"Failed to read {file_path}: {str(e)}")
        return csv_data

    def _get_optimal_tick_interval(self) -> int:
        total_tick_count = self.N_iter + 1
        max_display_ticks = 8
        tick_interval = max(1, (total_tick_count + max_display_ticks - 1) // max_display_ticks)
        return tick_interval

    def _plot_png_and_vector(
            self,
            csv_data: Dict[str, np.ndarray],
            par_indices: List[int],
            save_path: Path,
            nrows: int,
            ncols: int,
            obs_type: str
    ) -> None:
        if any(idx >= self.N_par or idx < 0 for idx in par_indices):
            raise IndexError("Parameter index exceeds the valid range")
        if len(par_indices) > nrows * ncols:
            raise ValueError(
                f"Number of subplots ({nrows * ncols}) is insufficient "
                f"to accommodate all parameters ({len(par_indices)})"
            )

        fig = plt.figure(figsize=(6 * ncols, 4 * nrows))
        gs = gridspec.GridSpec(nrows, ncols, figure=fig, hspace=0.4, wspace=0.2)
        axs = [fig.add_subplot(gs[i, j]) for i in range(nrows) for j in range(ncols)]
        colors = plt.cm.jet(np.linspace(0, 1, self.N_iter + 1))

        main_tick_interval = self._get_optimal_tick_interval()
        main_x_ticks = np.arange(0, (self.N_iter + 1) * self.N_e + 1, main_tick_interval * self.N_e)

        for idx, par_idx in enumerate(par_indices):
            ax = axs[idx]
            ax.autoscale(enable=False)
            for iter_idx in range(self.N_iter + 1):
                csv_key = self._get_csv_key(iter_idx, obs_type)
                if csv_key not in csv_data:
                    raise KeyError(f"Key not found in CSV data: {csv_key}. Please check if the file exists.")
                param_values = csv_data[csv_key][par_idx]
                x_range = np.arange(iter_idx * self.N_e + 1, (iter_idx + 1) * self.N_e + 1)
                ax.scatter(
                    x_range, param_values,
                    facecolors='white', edgecolors=colors[iter_idx],
                    linewidths=2, s=60, alpha=0.7
                )

            if (
                    self.best_par is not None
                    and len(self.best_par) > par_idx
                    and not np.isnan(self.best_par[par_idx])
            ):
                optimal_x = (self.N_iter + 1) * self.N_e + 1
                optimal_y = self.best_par[par_idx]
                ax.scatter(
                    optimal_x, optimal_y,
                    marker='x', color='darkblue', s=120, linewidths=2,
                    alpha=0.9, label='Best Value', clip_on=False, zorder=100
                )

            ax.set_xticks(main_x_ticks)
            ax.set_xticklabels([str(int(tick)) for tick in main_x_ticks], fontsize=16)
            ax.set_xlim(0, (self.N_iter + 1) * self.N_e + 2)
            ax.set_xlabel("Number of model evaluations", fontsize=16)
            ax.set_ylabel(self.par_name[par_idx], fontsize=16)
            ax.set_ylim(*self.param_range[par_idx])
            ax.yaxis.set_major_locator(MaxNLocator(prune='both', nbins=5))

        for ax in axs[len(par_indices):]:
            ax.axis('off')

        plt.subplots_adjust(top=0.90, bottom=0.08, left=0.05, right=0.95, hspace=0.4, wspace=0.2)

        png_path = save_path.with_suffix('.png')
        plt.savefig(png_path, dpi=300, bbox_inches='tight', format='png')
        logging.info(f"✅ Saved PNG image: {png_path.name}")
        plt.close()

    def _plot_sit(self, csv_data: Dict[str, np.ndarray], sit_indices: List[int], work_dir: Path, obs_type: str) -> None:
        if len(sit_indices) != 3:
            raise ValueError(
                f"Three site parameters are required, but {len(sit_indices)} were actually passed in."
            )
        base_save_path = work_dir / 'Figures' / f"{self.Optimization}-Site_Params"
        base_save_path.parent.mkdir(exist_ok=True, parents=True)
        self._plot_png_and_vector(csv_data, sit_indices, base_save_path, 1, 3, obs_type)

    def _plot_plant(
            self,
            csv_data: Dict[str, np.ndarray],
            plant_indices: List[int],
            obs_type: str,
            work_dir: Path
    ) -> None:
        plant_par_count = 11 if self.Stewart_Jarvis else 5
        expected_count = self.N_PLANT * plant_par_count
        if len(plant_indices) != expected_count:
            raise ValueError(
                f"The total number of plant parameters does not match: "
                f"{self.N_PLANT} × {plant_par_count} = {expected_count}, "
                f"but actual input is {len(plant_indices)}."
            )
        for i in range(self.N_PLANT):
            start_idx = i * plant_par_count
            end_idx = start_idx + plant_par_count
            base_save_path = work_dir / "Figures" / f"{self.Optimization}-PLANT{i + 1}_Params"
            base_save_path.parent.mkdir(exist_ok=True, parents=True)
            self._plot_png_and_vector(
                csv_data, plant_indices[start_idx:end_idx], base_save_path, 3, 4, obs_type
            )

    def _plot_residue(
            self,
            csv_data: Dict[str, np.ndarray],
            residue_indices: List[int],
            work_dir: Path,
            obs_type: str
    ) -> None:
        if len(residue_indices) != 3:
            raise ValueError(
                f"Three residue parameters are required, but {len(residue_indices)} were actually passed in."
            )
        base_save_path = work_dir / "Figures" / f"{self.Optimization}-Residue_Params"
        base_save_path.parent.mkdir(exist_ok=True, parents=True)
        self._plot_png_and_vector(csv_data, residue_indices, base_save_path, 1, 3, obs_type)

    def _plot_soil(
            self,
            csv_data: Dict[str, np.ndarray],
            soil_indices: List[int],
            work_dir: Path,
            obs_type: str
    ) -> None:
        expected_soil_params = self.N_layer * self.N_par_curve
        if len(soil_indices) != expected_soil_params:
            raise ValueError(
                f"The total number of soil parameters does not match: "
                f"{self.N_layer} × {self.N_par_curve} = {expected_soil_params}, "
                f"but actual input is {len(soil_indices)}."
            )
        base_save_path = work_dir / "Figures" / f"{self.Optimization}-Soil_Params"
        base_save_path.parent.mkdir(exist_ok=True, parents=True)
        self._plot_png_and_vector(
            csv_data, soil_indices, base_save_path, self.N_layer, self.N_par_curve, obs_type
        )

    def _plot_others(
            self,
            csv_data: Dict[str, np.ndarray],
            other_indices: List[int],
            work_dir: Path,
            obs_type: str
    ) -> None:
        if len(other_indices) != self.N_other_pars:
            raise ValueError(
                f"The number of other parameters does not match: "
                f"{self.N_other_pars} required, but {len(other_indices)} were actually passed in."
            )
        ncols = int(np.ceil(np.sqrt(self.N_other_pars)))
        nrows = int(np.ceil(self.N_other_pars / ncols))
        base_save_path = work_dir / "Figures" / f"{self.Optimization}-Other_Params"
        base_save_path.parent.mkdir(exist_ok=True, parents=True)
        self._plot_png_and_vector(csv_data, other_indices, base_save_path, nrows, ncols, obs_type)

    def plot_iteration_par(self, work_dir: str, obs_type: str,  best_par: Optional[List[float]],Optimization: str = 'ILUES') -> None:
        self.best_par = np.array(best_par) if best_par is not None else None
        self.Optimization = Optimization
        work_dir = Path(work_dir)
        csv_data = self._read_csv(str(work_dir), obs_type)
        other_indices: List[int] = []
        if self.N_other_pars > 0:
            other_indices = list(range(self.N_par - self.N_other_pars, self.N_par))

        if self.N_PLANT > 0 and self.Stewart_Jarvis and self.Residue:
            plant_par_count = 11
            sit_indices = [0, plant_par_count * self.N_PLANT + 4, plant_par_count * self.N_PLANT + 5]
            plant_indices = list(range(1, plant_par_count * self.N_PLANT + 1))
            residue_indices = list(range(plant_par_count * self.N_PLANT + 1, plant_par_count * self.N_PLANT + 4))
            soil_start = plant_par_count * self.N_PLANT + 6
            soil_end = soil_start + self.N_layer * self.N_par_curve
            soil_indices = list(range(soil_start, soil_end))
        elif self.N_PLANT > 0 and not self.Stewart_Jarvis and self.Residue:
            plant_par_count = 5
            sit_indices = [0, plant_par_count * self.N_PLANT + 4, plant_par_count * self.N_PLANT + 5]
            plant_indices = list(range(1, plant_par_count * self.N_PLANT + 1))
            residue_indices = list(range(plant_par_count * self.N_PLANT + 1, plant_par_count * self.N_PLANT + 4))
            soil_start = plant_par_count * self.N_PLANT + 6
            soil_end = soil_start + self.N_layer * self.N_par_curve
            soil_indices = list(range(soil_start, soil_end))
        elif self.N_PLANT > 0 and not self.Stewart_Jarvis and not self.Residue:
            plant_par_count = 5
            sit_indices = [0, plant_par_count * self.N_PLANT + 1, plant_par_count * self.N_PLANT + 2]
            plant_indices = list(range(1, plant_par_count * self.N_PLANT + 1))
            residue_indices = []
            soil_start = plant_par_count * self.N_PLANT + 3
            soil_end = soil_start + self.N_layer * self.N_par_curve
            soil_indices = list(range(soil_start, soil_end))
        elif self.N_PLANT == 0 and not self.Residue:
            sit_indices = [0, 1, 2]
            plant_indices = []
            residue_indices = []
            soil_start = 3
            soil_end = soil_start + self.N_layer * self.N_par_curve
            soil_indices = list(range(soil_start, soil_end))
        elif self.N_PLANT == 0 and self.Residue:
            sit_indices = [0, 4, 5]
            plant_indices = []
            residue_indices = list(range(1, 4))
            soil_start = 6
            soil_end = soil_start + self.N_layer * self.N_par_curve
            soil_indices = list(range(soil_start, soil_end))
        else:
            raise ValueError(
                f"Unsupported parameter combination: N_PLANT={self.N_PLANT}, "
                f"Stewart_Jarvis={self.Stewart_Jarvis}, Residue={self.Residue}"
            )

        total_par_count = (
                len(sit_indices) + len(plant_indices) + len(residue_indices) +
                len(soil_indices) + self.N_other_pars
        )
        if total_par_count != self.N_par:
            raise ValueError(
                f"Total parameter count mismatch: expected {self.N_par}, got {total_par_count}.\n"
                f"Breakdown: Site({len(sit_indices)}) + Plant({len(plant_indices)}) + "
                f"Residue({len(residue_indices)}) + Soil({len(soil_indices)}) + Others({self.N_other_pars})"
            )

        self._plot_sit(csv_data, sit_indices, work_dir, obs_type)
        if plant_indices:
            self._plot_plant(csv_data, plant_indices, obs_type, work_dir)
        if residue_indices:
            self._plot_residue(csv_data, residue_indices, work_dir, obs_type)
        self._plot_soil(csv_data, soil_indices, work_dir, obs_type)
        if other_indices:
            self._plot_others(csv_data, other_indices, work_dir, obs_type)

        logging.info("The SHAW model iteration parameter diagram has been fully drawn.")

    def _get_csv_key(self, iter_idx: int, obs_type: str) -> str:
        ensemble_dir = Path("Ensemble")
        if self.Optimization == 'ILUES':
            filename = f"ensemble_{iter_idx}_X_KL_f_{obs_type}.csv"
        elif self.Optimization == 'ESMDA':
            filename = f"ensemble_{iter_idx}_X_K_f_{obs_type}.csv"
        else:
            raise ValueError(f"Unsupported Optimization method: {self.Optimization}")
        return str(ensemble_dir / filename)
