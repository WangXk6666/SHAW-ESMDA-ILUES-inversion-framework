# SHAW-ESMDA-ILUES Inversion Framework

> **A Python-based parameter inversion framework coupling the SHAW model with the ESMDA and ILUES data assimilation algorithms.**
>
> **Author:** Xueke Wang (汪学科)  
> **Affiliation:** Chang'an University (长安大学)  
> **Email:** WangXk6666@outlook.com

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Dependencies](#-dependencies)
- [Usage](#-usage)
- [Repository Structure](#-repository-structure)
- [Copyright & Attribution](#️-copyright--attribution)
- [License](#-license)
- [Disclaimer](#️-disclaimer)
- [Contact](#-contact)
- [References](#-references)

---

## 🔬 Overview

This repository provides a parameter inversion framework that couples the **SHAW (Simultaneous Heat and Water) model** with two ensemble-based data assimilation algorithms:

- **ESMDA**: Ensemble Smoother with Multiple Data Assimilation, also written as ES-MDA.
- **ILUES**: Iterative Local Updating Ensemble Smoother.

The framework supports SHAW parameter estimation and posterior uncertainty analysis. It connects prior ensemble generation, batch SHAW simulations, iterative parameter updating, result evaluation, and visualization. The current application uses observations such as soil liquid water content and can evaluate posterior simulations of related variables such as soil temperature.

> **Important:** SHAW, ESMDA, and ILUES were developed by their respective original authors. This repository does not claim ownership of these third-party works. See [Copyright & Attribution](#️-copyright--attribution) for details.

---

## ✨ Features

### Core Inversion Workflow

- **SHAW model interface:** Runs SHAW forward simulations and reads model outputs.
- **ESMDA workflow:** Supports multiple assimilation iterations with configurable inflation factors.
- **ILUES workflow:** Uses local ensemble updates for nonlinear inverse problems.
- **Ensemble management:** Supports configurable ensemble size and iteration number.
- **Batch processing:** Automates model execution, parameter rewriting, and result collection.
- **Error handling:** Records SHAW execution errors and total runtime.

### Visualization and Post-processing

- Parameter marginal and joint distribution plots.
- Parameter trajectories across assimilation iterations.
- Posterior quantiles and ensemble uncertainty summaries.
- Time-series and soil-profile plots.
- RMSE, Nash-Sutcliffe efficiency (NSE), and coefficient of determination (R²).

---

## 📦 Dependencies

This project requires Python 3 and the following principal packages:

| Package | Minimum Version | Purpose |
| --- | ---: | --- |
| `numpy` | 1.21 | Numerical computation |
| `scipy` | 1.7 | Scientific computing and statistical distributions |
| `pandas` | 1.3 | Data processing and analysis |
| `matplotlib` | 3.4 | Static plotting and figure generation |
| `pyecharts` | 1.9 | Interactive visualization |
| `tqdm` | 4.62 | Progress bars |

Install the complete dependency set from `requirements.txt`.

The current workflow calls the Windows executable `SHAW303.EXE`. Native Linux execution is not provided in this repository.

---

## 📝 Usage

### 1. Download the Repository

Clone the repository:

```bash
git clone https://github.com/WangXk6666/SHAW-ESMDA-ILUES-inversion-framework.git
cd SHAW-ESMDA-ILUES-inversion-framework
```

Alternatively, download the repository as a ZIP file and extract it to a local directory.

### 2. Configure the Python Environment

Create and activate a virtual environment in Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 3. SHAW Model

Place `SHAW303.EXE` and the required SHAW input files in the location expected by `SHAW/SHAW_exe.py`. SHAW is not installed through `pip` and is not covered by this repository's MIT License.

### 4. Prepare the Experiment

Prepare the following files under `TEST_SHAW/Model/`:

- SHAW model configuration files.
- Meteorological forcing and boundary-condition files.
- Observation data.
- Prior parameter samples and parameter bounds.

Open `SHAW/RUNTHIS.py` and check:

- Ensemble size and number of assimilation iterations.
- Inflation factors and observation-error settings.
- Others

### 5. Run the Framework

Run the following command from the repository root:

```powershell
python SHAW/RUNTHIS.py
```

Numerical outputs are written to `TEST_SHAW/Ensemble/`, and figures are saved in `TEST_SHAW/Figures/`.

> **Note:** The example configuration uses an ensemble size of 20 and one assimilation iteration only to test whether the workflow runs correctly. These settings are not sufficient for scientific inference. Ensemble convergence and posterior stability must be evaluated for each application.

---

## 📁 Repository Structure

```text
SHAW-ESMDA-ILUES-inversion-framework/
├── General/
│   ├── __init__.py
│   ├── CriticalError.py        # Custom exception definitions
│   ├── draw_prior_sample.py    # Prior ensemble generation or import
│   ├── ES_K_update.py          # Ensemble smoother update
│   ├── local_update_for.py     # ILUES local update
│   └── obs_read.py             # Observation data reader
├── SHAW/
│   ├── __init__.py
│   ├── Clear.py                # Working-directory cleanup
│   ├── Error_SHAW.py           # SHAW execution error handling
│   ├── MAINPROGRESS.py         # Main workflow
│   ├── P.py                    # Parameter mapping
│   ├── RUNTHIS.py              # Algorithm settings and entry point
│   ├── SHAW_exe.py             # SHAW303.EXE runner
│   ├── SHAWParRewrite.py       # SHAW input file rewriting
│   ├── SHAWSimRead.py          # Standard SHAW output reader
│   ├── SingleResultReader.py   # Reader for selected outputs, such as ET
│   ├── SoluteReader.py         # Solute output reader
│   ├── TIMECOUNT.py            # Runtime tracking
│   └── WaterBalanceReader.py   # Water-balance output reader
├── SHAWFinalResult/
│   ├── __init__.py
│   ├── Distribution.py         # Parameter distribution plots
│   ├── PlotIterationPar.py     # Parameter iteration plots
│   ├── PlotResult.py           # Simulation result plots
│   ├── Quantile.py             # Posterior quantiles
│   └── ReadFinal.py            # Final result reader
├── TEST_SHAW/
│   ├── Ensemble/               # Ensemble results and posterior summaries
│   ├── Figures/                # Generated figures
│   └── Model/                  # SHAW inputs and working files
├── requirements.txt
├── README.md
└── LICENSE
```

Do not rename SHAW input or output files unless the corresponding paths and readers are updated. Keep a backup of the original model input files because the framework rewrites parameters during ensemble simulations.

### Example Outputs

| Output | Description |
| --- | --- |
| `ensemble_*_X_K_f_moi.csv` | Simulated liquid water content for all ensemble members |
| `ensemble_*_X_K_f_temp.csv` | Simulated soil temperature for all ensemble members |
| `Quantile_moi.csv` | Posterior interval for liquid water content |
| `Quantile_temp.csv` | Posterior interval for soil temperature |
| `joint_distribution_*.png` | Joint posterior parameter distribution |

---

## ⚖️ Copyright & Attribution

This repository contains original integration, workflow, input/output processing, evaluation, and visualization code written by Xueke Wang. It also uses or interfaces with the following third-party research products:

### 1. SHAW Model

- **Original developer:** Gerald N. Flerchinger and collaborators, USDA Agricultural Research Service.
- **Official source:** [USDA-ARS SHAW Model](https://www.ars.usda.gov/pacific-west-area/boise-id/northwest-watershed-research-center/docs/shaw-model/).
- **Requirement:** The SHAW program, documentation, and associated files retain their original notices and terms and are not covered by this repository's MIT License.

### 2. ESMDA

- **Original developers:** Alexandre A. Emerick and Albert C. Reynolds.
- **Original publication:** Emerick and Reynolds (2013).
- **Requirement:** The ESMDA method and any third-party implementation retain their original attribution, copyright notices, and license terms.

### 3. ILUES

- **Original developers:** Jiangjiang Zhang and co-authors.
- **Original publication:** Zhang et al. (2018).
- **Requirement:** The ILUES method and any third-party implementation retain their original attribution, copyright notices, and license terms.

The original authors do not necessarily endorse this repository. Academic citation acknowledges the underlying research but does not replace any permission required to redistribute third-party source code or executable files.

---

## 📜 License

The [MIT License](LICENSE) applies only to code for which Xueke Wang owns the copyright. It does not relicense the SHAW model, SHAW documentation, or third-party ESMDA and ILUES implementations. All original copyright and license notices must be retained.

---

## ⚠️ Disclaimer

This software is provided "as is", without warranty of any kind. Inversion results depend on the input data, model configuration, prior parameter distributions, observation-error assumptions, ensemble size, and algorithm settings. Users are responsible for testing convergence and validating results before scientific or operational use.

---

## 📬 Contact

- **Author:** Xueke Wang (汪学科)
- **Institution:** Chang'an University (长安大学)
- **Email:** WangXk6666@outlook.com
- **GitHub:** [WangXk6666](https://github.com/WangXk6666)

For reproducible bug reports, open a GitHub Issue and include the operating system, Python version, relevant configuration, and complete error traceback.

---

## 📚 References

### SHAW Model

1. Flerchinger, G. N., and Saxton, K. E. (1989). Simultaneous heat and water model of a freezing snow-residue-soil system. I. Theory and development. *Transactions of the ASAE*, 32(2), 565-571.
2. Flerchinger, G. N., and Saxton, K. E. (1989). Simultaneous heat and water model of a freezing snow-residue-soil system. II. Field verification. *Transactions of the ASAE*, 32(2), 573-578.
3. Flerchinger, G. N. (2000). *The Simultaneous Heat and Water (SHAW) Model: Technical Documentation*. Technical Report NWRC 2000-09, USDA Agricultural Research Service.
4. Flerchinger, G. N., Caldwell, T. G., Cho, J., and Hardegree, S. P. (2012). Simultaneous Heat and Water Model: Model use, calibration, and validation. *Transactions of the ASABE*, 55(4), 1395-1411. https://doi.org/10.13031/2013.42250

### ESMDA

5. Emerick, A. A., and Reynolds, A. C. (2013). Ensemble smoother with multiple data assimilation. *Computers & Geosciences*, 55, 3-15. https://doi.org/10.1016/j.cageo.2012.03.011
6. Emerick, A. A., and Reynolds, A. C. (2012). History matching time-lapse seismic data using the ensemble Kalman smoother with multiple data assimilation. *Computational Geosciences*, 16(3), 639-659. https://doi.org/10.1007/s10596-012-9275-5

### ILUES

7. Zhang, J., Lin, G., Li, W., Wu, L., and Zeng, L. (2018). An iterative local updating ensemble smoother for estimation and uncertainty assessment of hydrologic model parameters with multimodal distributions. *Water Resources Research*, 54(3), 1716-1733. https://doi.org/10.1002/2017WR020906

---

