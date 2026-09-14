SHAW–ESMDA–ILUES Parameter Inversion Framework

A Python workflow for parameter estimation and uncertainty analysis that couples the Simultaneous Heat and Water (SHAW) model with ESMDA and ILUES.

Author: Xueke Wang (汪学科)
Affiliation: Chang'an University (长安大学)
Email: WangXk6666@outlook.com

[!IMPORTANT]
This repository provides integration, workflow, and post-processing code. The SHAW model and the ESMDA and ILUES methods and implementations are third-party works developed by their respective authors. The repository author does not claim ownership of these components. Their original copyright notices, licenses, and citation requirements must be retained. Cite the original publications listed in References when using this framework in research.

Table of Contents

Overview

Features

Requirements

Installation

Quick Start

Configuration

Outputs

Repository Structure

Citation

Third-Party Software and Attribution

License

Disclaimer

Contact

References

Overview

This repository links the one-dimensional SHAW model to two ensemble-smoother algorithms:

ESMDA (Ensemble Smoother with Multiple Data Assimilation; often written ES-MDA) repeatedly assimilates the same observations using inflated observation-error covariance.

ILUES (Iterative Local Updating Ensemble Smoother) updates a local ensemble for each sample and is designed for nonlinear inverse problems that may have multimodal parameter distributions.

The workflow supports prior-ensemble generation, batch SHAW simulations, iterative parameter updating, result aggregation, uncertainty summaries, and publication-oriented visualization. It was developed for SHAW parameter inversion using observations such as soil liquid water content and for evaluating posterior simulations of related state variables such as soil temperature.

Features

Inversion workflow

Interface for running SHAW 3.03 (SHAW303.EXE)

ESMDA and ILUES parameter-update workflows

Configurable ensemble size and number of assimilation iterations

Batch execution and error handling for ensemble simulations

Prior and posterior parameter management

Post-processing

Marginal and joint parameter-distribution plots

Parameter trajectories across assimilation iterations

Posterior quantiles and ensemble-spread summaries

Time-series and soil-profile plots

RMSE, Nash–Sutcliffe efficiency (NSE), and coefficient of determination (R²)

Requirements

System requirements

Python 3

A local copy of SHAW 3.03 obtained from the official USDA-ARS website

An operating system capable of running SHAW303.EXE

The current workflow calls a Windows executable. Native Linux execution has not been documented for this repository.

Python dependencies

Install the exact dependency set from requirements.txt. The principal packages are:

Package

Minimum version

Purpose

numpy

1.21

Numerical computation

scipy

1.7

Scientific computing and probability distributions

pandas

1.3

Tabular data processing

matplotlib

3.4

Static visualization

pyecharts

1.9

Interactive visualization

tqdm

4.62

Progress reporting

Installation

Clone the repository:

git clone https://github.com/WangXk6666/SHAW-ESMDA-ILUES-inversion-framework.git
cd SHAW-ESMDA-ILUES-inversion-framework

Create and activate a virtual environment. On Windows PowerShell:

py -m venv .venv
.venv\Scripts\Activate.ps1

Install the dependencies:

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

Download SHAW 3.03 from the official USDA-ARS SHAW page. Place the executable and the required SHAW input files in the model directory expected by SHAW/SHAW_exe.py.

[!NOTE]
SHAW is not installed through pip. Its executable, documentation, sample inputs, and any applicable notices must be obtained separately from USDA-ARS.

Quick Start

Prepare the SHAW configuration, meteorological forcing, boundary conditions, observations, and prior parameter samples under TEST_SHAW/Model/.

Open SHAW/RUNTHIS.py and check all paths and algorithm settings.

Run the workflow from the repository root:

python SHAW/RUNTHIS.py

Review numerical outputs in TEST_SHAW/Ensemble/ and figures in TEST_SHAW/Figures/.

The example configuration uses an ensemble size of 20 and one assimilation iteration to provide a quick smoke test.

[!WARNING]
The demonstration settings are intentionally small and are not sufficient for scientific inference. Convergence, ensemble size, observation-error assumptions, prior ranges, and posterior stability must be evaluated for each application.

Configuration

Before starting an inversion, verify the following items in SHAW/RUNTHIS.py and the associated input files:

algorithm selection: ESMDA or ILUES;

ensemble size and number of assimilation iterations;

inflation factors and observation-error settings;

parameter names, bounds, transformations, and mappings to SHAW inputs;

observation variables, depths, times, units, and missing-value handling;

paths to the SHAW executable, model inputs, and output directories; and

consistency between the SHAW simulation period and the observation period.

Keep an untouched copy of the original SHAW input files. The workflow rewrites model inputs for individual ensemble members during execution.

Outputs

The workflow produces iteration-specific ensemble files, posterior summaries, and diagnostic figures. Common outputs include:

Output

Description

ensemble_*_X_K_f_moi.csv

Simulated liquid-water-content ensemble after an update

ensemble_*_X_K_f_temp.csv

Simulated soil-temperature ensemble used for independent evaluation

Quantile_moi.csv

Posterior quantiles for liquid water content

Quantile_temp.csv

Posterior quantiles for soil temperature

PlotIterationPar.py

Parameter-trajectory visualization

Distribution.py

Marginal or joint parameter-distribution visualization

PlotResult.py

Simulation-result and uncertainty visualization

Output names may include the assimilation iteration or algorithm identifier. Inspect the scripts before changing filenames because downstream post-processing routines may rely on the existing naming convention.

Repository Structure

SHAW-ESMDA-ILUES-inversion-framework/
├── General/
│   ├── __init__.py
│   ├── CriticalError.py        # Custom exception definitions
│   ├── draw_prior_sample.py    # Prior-ensemble generation or import
│   ├── ES_K_update.py          # Ensemble-smoother parameter update
│   ├── local_update_for.py     # ILUES local-update routine
│   └── obs_read.py             # Observation-data reader
├── SHAW/
│   ├── __init__.py
│   ├── Clear.py                # Working-directory cleanup
│   ├── Error_SHAW.py           # SHAW execution-error handling
│   ├── MAINPROGRESS.py         # Main inversion workflow
│   ├── P.py                    # Parameter mapping
│   ├── RUNTHIS.py              # User configuration and entry point
│   ├── SHAW_exe.py             # SHAW303.EXE runner
│   ├── SHAWParRewrite.py       # SHAW input-file rewriting
│   ├── SHAWSimRead.py          # Standard SHAW output reader
│   ├── SingleResultReader.py   # Reader for selected outputs, such as ET
│   ├── SoluteReader.py         # Solute-output reader
│   ├── TIMECOUNT.py            # Runtime tracking
│   └── WaterBalanceReader.py   # Water-balance output reader
├── SHAWFinalResult/
│   ├── __init__.py
│   ├── Distribution.py
│   ├── PlotIterationPar.py
│   ├── PlotResult.py
│   ├── Quantile.py
│   └── ReadFinal.py
├── TEST_SHAW/
│   ├── Ensemble/               # Ensemble states, parameters, and summaries
│   ├── Figures/                # Diagnostic and publication-oriented figures
│   └── Model/                  # SHAW inputs and working files
├── requirements.txt
├── README.md
└── LICENSE

Do not rename SHAW input or output files unless the corresponding paths and readers are updated. Their contents should be adapted to the study site and experiment.

Citation

If this repository contributes to a publication, cite both the framework and the original SHAW, ESMDA, and/or ILUES papers relevant to the analysis.

Suggested citation for this repository:

@software{wang_shaw_esmda_ilues_2026,
  author  = {Wang, Xueke},
  title   = {SHAW--ESMDA--ILUES Parameter Inversion Framework},
  year    = {2026},
  url     = {https://github.com/WangXk6666/SHAW-ESMDA-ILUES-inversion-framework}
}

For reproducible citation, create a tagged release and replace the repository URL above with the release DOI if the release is archived through Zenodo or another repository.

Third-Party Software and Attribution

Component

Original contribution

Copyright and license treatment

SHAW

Developed by Gerald N. Flerchinger and collaborators at USDA-ARS

The SHAW program, documentation, and associated files remain the work of USDA-ARS and their original authors. They are not covered by this repository's MIT License. Obtain SHAW from the official SHAW page and retain all notices and terms supplied with it.

ESMDA

Method introduced by Emerick and Reynolds (2013)

The ESMDA method and any third-party implementation included or adapted in this project remain attributable to their original authors. The original copyright and license notices must be retained, and the ESMDA code is excluded from this repository's MIT License unless its own license explicitly states otherwise.

ILUES

Method introduced by Zhang et al. (2018)

The ILUES method and any third-party implementation included or adapted in this project remain attributable to Zhang and co-authors. The original copyright and license notices must be retained, and the ILUES code is excluded from this repository's MIT License unless its own license explicitly states otherwise.

These attributions do not imply endorsement by the original authors. Academic citation acknowledges the underlying research, whereas redistribution of executable files or source code is governed by the applicable software license or explicit permission. When no redistribution license has been provided, users must obtain the component from its official source or secure permission from the copyright holder.

License

Only the original integration and extension code written by Xueke Wang is released under the MIT License. This includes author-owned workflow control, SHAW coupling, parameter mapping, input/output processing, result evaluation, and visualization code. The MIT License permits academic and commercial use, modification, and redistribution of this author-owned code, provided that its copyright and license notice are retained.

The MIT License does not apply to the SHAW model, its executable or documentation, or third-party ESMDA and ILUES implementations. Those components retain their original copyright, license, and permission requirements. Any corresponding source-code headers and license files must remain intact when redistribution is permitted.

Disclaimer

This research software is provided "as is", without warranty of any kind. The accuracy of an inversion depends on the model configuration, forcing and observation data, prior parameter distributions, observation-error model, ensemble size, and algorithm settings. Users are responsible for testing convergence, checking mass and energy balances where relevant, and validating results before scientific or operational use.

Contact

Xueke Wang: WangXk6666@outlook.com

GitHub: @WangXk6666

SHAW support: ARS-BOISE-DATA@usda.gov

Please use GitHub Issues for reproducible bug reports. Include the operating system, Python version, relevant settings, and the complete error traceback, but do not upload confidential data.

References

Flerchinger, G. N., & Saxton, K. E. (1989). Simultaneous heat and water model of a freezing snow-residue-soil system. I. Theory and development. Transactions of the ASAE, 32(2), 565–571.

Flerchinger, G. N., & Saxton, K. E. (1989). Simultaneous heat and water model of a freezing snow-residue-soil system. II. Field verification. Transactions of the ASAE, 32(2), 573–578.

Flerchinger, G. N. (2000). The Simultaneous Heat and Water (SHAW) Model: Technical Documentation (Technical Report NWRC 2000-09). USDA Agricultural Research Service, Northwest Watershed Research Center.

Flerchinger, G. N., Caldwell, T. G., Cho, J., & Hardegree, S. P. (2012). Simultaneous Heat and Water Model: Model use, calibration, and validation. Transactions of the ASABE, 55(4), 1395–1411. https://doi.org/10.13031/2013.42250

Emerick, A. A., & Reynolds, A. C. (2013). Ensemble smoother with multiple data assimilation. Computers & Geosciences, 55, 3–15. https://doi.org/10.1016/j.cageo.2012.03.011

Emerick, A. A., & Reynolds, A. C. (2012). History matching time-lapse seismic data using the ensemble Kalman smoother with multiple data assimilation. Computational Geosciences, 16(3), 639–659. https://doi.org/10.1007/s10596-012-9275-5

Zhang, J., Lin, G., Li, W., Wu, L., & Zeng, L. (2018). An iterative local updating ensemble smoother for estimation and uncertainty assessment of hydrologic model parameters with multimodal distributions. Water Resources Research, 54(3), 1716–1733. https://doi.org/10.1002/2017WR020906
