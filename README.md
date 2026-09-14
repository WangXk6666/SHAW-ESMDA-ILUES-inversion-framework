# SHAW-ESMDA-ILUES Inversion Framework

> **A Python-based parameter inversion framework integrating the SHAW model with ESMDA/ILUES data assimilation algorithms, featuring comprehensive visualization and evaluation tools.**
>
> **Author**: Wang Xueke (汪学科)  
> **Affiliation**: Chang'an University (长安大学)  
> **Email**: WangXk6666@outlook.com  
> **Date**: 2026-06-16

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Dependencies](#dependencies)
- [Usage](#usage)
- [Repository Structure](#repository-structure)
- [Copyright & Attribution](#copyright--attribution)
- [License](#license)
- [Disclaimer](#disclaimer)
- [Contact](#contact)
- [References](#references)

---

## 🔬 Overview

This repository provides a complete **parameter inversion framework** that couples the **SHAW (Simultaneous Heat and Water) model** with two state-of-the-art ensemble-based data assimilation algorithms: **ESMDA (Ensemble Smoother with Multiple Data Assimilation)** and **ILUES (Iterative Local Updating Ensemble Smoother)**.

The framework is designed for hydrological and land-surface modeling applications, enabling efficient calibration of SHAW model parameters through ensemble-based Bayesian inversion. In addition to the core inversion pipeline, this repository includes a rich suite of **post-processing tools** for:

- Parameter joint distribution visualization
- Parameter iteration trajectory plotting
- Comprehensive result evaluation metrics
- Publication-ready figure generation

> ⚠️ **Important Notice**: This framework is an **integration and extension work** developed by the author. The SHAW model, ESMDA algorithm, and ILUES algorithm are **NOT** developed by the author. Please refer to the [Copyright & Attribution](#copyright--attribution) section for detailed ownership information.

---

## ✨ Features

### Core Inversion Pipeline
- **SHAW Model Interface**: Seamless coupling with the SHAW model for forward simulations
- **ESMDA Integration**: Multiple data assimilation with adaptive inflation factors
- **ILUES Integration**: Local ensemble updating for multimodal parameter distributions
- **Ensemble Management**: Configurable ensemble size

### Visualization & Post-processing
- 📊 **Joint Distribution Plots**: Parameter posterior joint probability distributions
- 📈 **Iteration Trajectory Plots**: Parameter convergence over assimilation iterations
- 🎯 **Evaluation Metrics**: RMSE, NSE, R²
- 🗺️ **Spatial/Temporal Visualization**: Time-series and profile plotting capabilities

### Additional Tools
- Automated result aggregation and summary
- Statistical analysis of ensemble spread
- Sensitivity analysis utilities
- Batch processing support

---

## 📦 Dependencies

This project requires the following Python packages:

| Package | Version | Purpose |
|---------|---------|---------|
| `numpy` | ≥1.21 | Numerical computations |
| `scipy` | ≥1.7 | Scientific computing, statistical distributions |
| `pandas` | ≥1.3 | Data manipulation and analysis |
| `matplotlib` | ≥3.4 | Static plotting and figure generation |
| `pyecharts` | ≥1.9 | Interactive web-based visualizations |
| `tqdm` | ≥4.62 | Progress bars for long-running processes |


## 📝 Usage

1. **下载压缩包*
   下载压缩包后，保存到本地的项目文件之后进行解压

2. **配置环境**
使用Python的IDE打开项目文件后，按照Requirements.txt配置环境

3. **程序运行**
   打开SHAW/RUNTHIS.py设置相应的算法配置后即可运行，为了节省时间，本程序中仅设置集合大小为20，迭代次数为1次来检测程序
---



## 📁 Repository Structure

```
SHAW-ESMDA-ILUES-inversion-framework/
├── General/
│   ├── __init__.py             
│   ├── CriticalError.py       # ESMDA implementation
│   ├── draw_prior_sample.py   # Default is reading the prior sample.csv in Model direction
│   ├── ES_K_update.py         # ESMDA implementation
│   ├── local_update_for.py    # ILUES implementation
│   └── obs_read.py            # Reading observation data in Model direction
├── SHAW/
│   ├── __init__.py
│   ├── Clear.py               # Clearing work direction
│   ├── Error_SHAW.py          # Handling the error in Model execution 
│   ├── MAINPROGRESS.py        # Main workflow
│   ├── P.py                   # 参数映射
│   ├── RUNTHIS.py             # 算法设置和主程序运行
│   ├── SHAW_exe.py            # Running SHAW303.EXE
│   ├── SHAWParRewrite.py      # Rewriting new parameters into Model confrigution
│   ├── SHAWSimRead.py         # Reading Simulation Results by SHAW model's output files
│   ├── SingleResultReader.py  # Reading Simulation Results by SHAW model's output files, Likes ET...
│   ├── SoluteReader.py        # Reading Simulation Results by SHAW model's solution output files
│   ├── TIMECOUNT.py           # 记录整个程序的运行时间
│   └── WaterBalanceReader.py  # Reading Simulation Results by SHAW model's Water balance output files
├── SHAWFinalResult/           
│   ├── __init__.py
│   ├── Distribution.py
│   ├── PlotIterationPar.py
│   ├── PlotResult.py
│   ├── Quantile.py
│   └── ReadFinal.py
├── TEST_SHAW/                # Model and its output files
│   ├── Ensemble/             # csv files of different results, like updated parameters and varibles
│   │   ├── ensemble_1_X_K_f_moi.csv # 同化变量（液态水含量）的结果，每列代表一个样本
│   │   ├── ensemble_1_X_K_f_temp.csv # 参考变量（温度）的结果，每列代表一个样本
│   │   ... 
│   │   ├── Quantile_moi.csv # 同化变量（液态水含量）95%后验区间的结果
│   │   └── Quantile_moi.csv # 参考变量（土壤温度）95%后验区间的结果
│   │
│   ├── Figures               # Visualization of different results
│   │   ├── conbined_results_k.png # 所有样本的的评估指标（仅供初步判断）
│   │   ├── ensemble_1_X_K_f_moi.png #同化变量（液态水含量）95%后验区间的结果 
│   │   ... 
│   │   ├── ILUES-Site_Params.png # 地表参数的迭代过程
│   │   └── joint_distribution_k.png # ESMDA算法后验参数的joint distribution
│   │
│   └── Model                 # Configuration files of SHAW model(Don't change the name of these files but content)
├── 
├── requirements.txt
├── README.md                  # This file
└── LICENSE                    # License file
```

---

## ⚖️ Copyright & Attribution

### Important Copyright Notice

This repository contains **original code developed by the author** for the integration, visualization, and evaluation components. However, the following third-party components are **NOT** the intellectual property of the author and are subject to their respective copyrights:

#### 1. SHAW Model (Simultaneous Heat and Water)
- **Copyright Holder**: United States Department of Agriculture (USDA), Agricultural Research Service (ARS)
- **Original Developer**: Dr. Gerald N. Flerchinger, USDA-ARS Northwest Watershed Research Center, Boise, Idaho
- **Original Publication**: Flerchinger, G.N. and Saxton, K.E. (1989). "Simultaneous heat and water model of a freezing snow-residue-soil system I. Theory and development." *Transactions of the ASAE*, 32(2), 565-571.
- **Official Source**: https://www.ars.usda.gov/pacific-west-area/boise-id/northwest-watershed-research-center/docs/shaw-model/
- **Download**: ftp://ftp.nwrc.ars.usda.gov/public/ShawModel/
- **Status**: Public domain (U.S. Government work); users must obtain the model directly from USDA-ARS

#### 2. ESMDA Algorithm (Ensemble Smoother with Multiple Data Assimilation)
- **Copyright Holder**: Original authors
- **Original Developers**: Alexandre A. Emerick and Albert C. Reynolds, The University of Tulsa, Petroleum Reservoir Exploitation Projects
- **Original Publication**: Emerick, A.A. and Reynolds, A.C. (2013). "Ensemble smoother with multiple data assimilation." *Computers & Geosciences*, 55, 3-15. DOI: 10.1016/j.cageo.2012.03.011
- **Reference**: Emerick, A.A. and Reynolds, A.C. (2012). "History matching time-lapse seismic data using the ensemble Kalman smoother with multiple data assimilation." *Computational Geosciences*, 16(3), 639-659. DOI: 10.1007/s10596-012-9275-5
- **Note**: The ESMDA algorithm implementation in this repository is an independent Python re-implementation based on the published mathematical formulations. The original algorithm and its theoretical foundation remain the intellectual property of Emerick and Reynolds.

#### 3. ILUES Algorithm (Iterative Local Updating Ensemble Smoother)
- **Copyright Holder**: Dr. Jiangjiang Zhang and co-authors
- **Original Developer**: Dr. Jiangjiang Zhang (张江江), Professor, Hohai University (河海大学), Yangtze Institute for Conservation and Development, Nanjing, China
- **Affiliation at Time of Publication**: College of Environmental and Resource Sciences, Zhejiang University; currently at Hohai University
- **Original Publication**: Zhang, J., Lin, G., Li, W., Zeng, L., and Wu, L. (2018). "An iterative local updating ensemble smoother for estimation and uncertainty assessment of hydrologic model parameters with multimodal distributions." *Water Resources Research*, 54(3), 1716-1733. DOI: 10.1002/2017WR021296
- **Preprint**: arXiv:1611.04702 [stat.CO] (2016)
- **Contact**: zhangjiangjiang@hhu.edu.cn
- **Note**: The ILUES algorithm implementation in this repository is an independent Python re-implementation based on the published mathematical formulations. The original algorithm and its theoretical foundation remain the intellectual property of Dr. Jiangjiang Zhang and co-authors.

### Author's Contribution
- **Integration Framework**: Coupling SHAW model with ESMDA/ILUES algorithms
- **Visualization Tools**: Joint distribution plots, iteration trajectory plots, evaluation plots, interactive charts
- **Evaluation Metrics**: Comprehensive statistical metrics computation
- **Workflow Automation**: End-to-end parameter inversion pipeline
- **Documentation**: User guides and examples

### Usage Requirements
By using this software, you agree to:
1. **Cite the original authors** of SHAW, ESMDA, and ILUES in any publication or presentation resulting from the use of this framework.
2. **Obtain the SHAW model** directly from the official USDA-ARS source.
3. **Acknowledge** this framework (Wang Xueke, Chang'an University) if the integration code is used.
4. **Not claim ownership** or register copyrights over the SHAW model, ESMDA algorithm, or ILUES algorithm.

---

## 📜 License

This project is licensed under the **MIT License** for the original code written by the author. See [LICENSE](LICENSE) for details.

**However**, the following restrictions apply:

- The **SHAW model** is a U.S. Government work and is in the public domain, but must be obtained from the official USDA-ARS source.
- The **ESMDA algorithm** and **ILUES algorithm** are subject to the copyrights of their respective original authors.
- This framework **does NOT include** the SHAW model source code, ESMDA original code, or ILUES original code.
- Users must comply with the licensing terms of all third-party dependencies (numpy, scipy, pandas, matplotlib, pyecharts, tqdm).

### Permitted Use
- ✅ Academic research and educational purposes
- ✅ Personal learning and experimentation
- ✅ Citation and reference in academic publications

### Prohibited Use
- ❌ Commercial use without proper attribution
- ❌ Registration of copyright or patent claims over the SHAW model, ESMDA, or ILUES
- ❌ Redistribution of the SHAW model without USDA-ARS permission
- ❌ Claiming authorship of the original algorithms or model

---

## ⚠️ Disclaimer

THIS SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

The author makes no representations about the suitability of this software for any purpose. The accuracy of inversion results depends on the quality of input data, model configuration, and parameter settings. Users are responsible for validating results before using them for decision-making.

---

## 📬 Contact

- **Author**: Wang Xueke (汪学科)
- **Institution**: Chang'an University (长安大学)
- **Email**: WangXk6666@outlook.com
- **GitHub**: [@WangXk6666](https://github.com/WangXk6666)

For questions regarding:
- **SHAW model**: Contact Dr. Gerald Flerchinger (gerald.flerchinger@usda.gov) or visit [USDA-ARS SHAW Model Page](https://www.ars.usda.gov/pacific-west-area/boise-id/northwest-watershed-research-center/docs/shaw-model/)
- **ESMDA algorithm**: Refer to publications by Emerick & Reynolds (2013)
- **ILUES algorithm**: Contact Dr. Jiangjiang Zhang (zhangjiangjiang@hhu.edu.cn)

---

## 📚 References

### SHAW Model
1. Flerchinger, G.N. and Saxton, K.E. (1989). "Simultaneous heat and water model of a freezing snow-residue-soil system I. Theory and development." *Transactions of the ASAE*, 32(2), 565-571.
2. Flerchinger, G.N. and Saxton, K.E. (1989). "Simultaneous heat and water model of a freezing snow-residue-soil system II. Field verification." *Transactions of the ASAE*, 32(2), 573-578.
3. Flerchinger, G.N. (2000). "The Simultaneous Heat and Water (SHAW) Model: Technical Documentation." Technical Report NWRC 2000-09, USDA-ARS Northwest Watershed Research Center, Boise, Idaho.
4. Flerchinger, G.N., Reba, M.L., and Links, T.E. (2012). "Simultaneous heat and water (SHAW) model: model use, calibration, and validation." *Transactions of the ASABE*, 55(4), 1395-1411.
5. **Official Website**: https://www.ars.usda.gov/pacific-west-area/boise-id/northwest-watershed-research-center/docs/shaw-model/

### ESMDA Algorithm
6. Emerick, A.A. and Reynolds, A.C. (2013). "Ensemble smoother with multiple data assimilation." *Computers & Geosciences*, 55, 3-15. DOI: 10.1016/j.cageo.2012.03.011
7. Emerick, A.A. and Reynolds, A.C. (2012). "History matching time-lapse seismic data using the ensemble Kalman smoother with multiple data assimilation." *Computational Geosciences*, 16(3), 639-659. DOI: 10.1007/s10596-012-9275-5

### ILUES Algorithm
8. Zhang, J., Lin, G., Li, W., Zeng, L., and Wu, L. (2018). "An iterative local updating ensemble smoother for estimation and uncertainty assessment of hydrologic model parameters with multimodal distributions." *Water Resources Research*, 54(3), 1716-1733. DOI: 10.1002/2017WR021296
9. Zhang, J., et al. (2016). "An iterative local-updating ensemble smoother for high-dimensional inverse modeling with multimodal distributions." arXiv:1611.04702 [stat.CO].

### This Framework
10. Wang, X. (2026). "SHAW-ESMDA-ILUES Inversion Framework." GitHub Repository. https://github.com/WangXk6666/SHAW-ESMDA-ILUES-inversion-framework

---

<div align="center">

**⭐ If you find this framework helpful, please consider giving it a star!**

*Last updated: 2026-06-16*

</div>
