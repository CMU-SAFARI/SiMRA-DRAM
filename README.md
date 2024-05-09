# Simultaneous Many-Row Activation in Off-the-Shelf DRAM Chips: Experimental Characterization and Analysis


<p align=center>
<img src="https://dsn2024uq.github.io/images/dsn2024_artifact.png" alt="Code and data reproduced" width="600">
</p>


[![Academic Code](https://img.shields.io/badge/Origin-Academic%20Code-C1ACA0.svg?style=flat)]() [![Language Badge](https://img.shields.io/badge/Made%20with-C/C++-blue.svg)](https://isocpp.org/std/the-standard) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![contributions welcome](https://img.shields.io/badge/Contributions-welcome-lightgray.svg?style=flat)]() [![Preprint: arXiv](https://img.shields.io/badge/cs.AR-2402.18736-b31b1b?logo=arxiv&logoColor=red)](https://arxiv.org/pdf/2405.XXXX.pdf) 

This repository provides the source code of our [DSN'24 paper](https://arxiv.org/pdf/XXXX.pdf):

> Ismail Emir Yüksel, Yahya Can Tugrul, F. Nisa Bostancı, Geraldo F. Oliveira, A. Giray Yaglıkçı, Ataberk Olgun, Melina Soysal, Haocong Luo, Juan Gómez-Luna, Mohammad Sadrosadati, Onur Mutlu, "Simultaneous Many-Row Activation in Off-the-Shelf DRAM Chips: Experimental Characterization and Analysis", DSN'24.



Please use the following citation to cite our study if the repository is useful for you.
```
@inproceedings{yuksel2024simultaneous,
    title={{Functionally-Complete Boolean Logic in Real DRAM Chips: Experimental Characterization and Analysis}},
    author={Yuksel, Ismail Emir and Tugrul, Yahya Can and Bostanci, F. Nisa and de Oliveira, Geraldo F. and Yaglikci, A. Giray and Olgun, Ataberk and Soysal, Melina and Luo, Haocong and Luna, Juan Gomez and Sadrosadati, Mohammad and Mutlu, Onur},
    year={2024},
    booktitle={{DSN}}
}
```

## Prerequisite
Our real DRAM chip characterization is based on the open-source FPGA-based DRAM characterization infrastructure [DRAM Bender](https://github.com/CMU-SAFARI/DRAM-Bender). Please check out and follow the installation instructions of [DRAM Bender](https://github.com/CMU-SAFARI/DRAM-Bender).

The software dependencies for the characterization are:
- GNU Make, CMake 3.10+
- `c++-17` build toolchain (tested with `gcc-9`)
- Python 3.9+
- `pip` packages `pandas`, `scipy`, `matplotlib`, and `seaborn`

## Hardware Setup
Our real DRAM chip characterization infrastructure consists of the following components:
- A host x86 machine with a PCIe 3.0 x16 slot
- An FPGA board with a DIMM/SODIMM slot supported by [DRAM Bender](https://github.com/CMU-SAFARI/DRAM-Bender) (e.g., Xilinx Alveo U200)
- Heater pads attached to the DRAM module under test
- A temperature controller (e.g., MaxWell FT200) programmable by the host machine connected to the heater pads

## Directory Structure
```
DRAM-Bender           # A fork of DRAM Bender that contains the characterization program
  └ sources           
    └ apps           
      └ DSN_AE_APPS    # Source code of the characterization program    
└ analysis              # Scripts to aggregate, analyze, and plot the characterization data
  └ plots               # Jupyter notebooks to plot the data
  └ scripts             # Shell scripts to aggregate 
  and analyze the data
└ experimental_data            # Directory that contains all experimental data (download the files from Zenodo)
  └ existing_all_data              # data we obtained for our submission
  └ existing_all_data_except_tested_module               # submission data without one tested module
  └ existing_data_tested_module               # excluded tested module's submission data
  └ new_data_tested_module               # data obtained from the reader (initally empty)

```
## Running Characterization Experiments

### Expected Time
We expect comprehensively reproducing experimental data listed above (for one temperature and voltage level) for one module to take approximately more than a week.

### Step 0
The real DRAM chip characterization takes a long period of time. To run all our characterization experiments, a completion time of 1-2 weeks is expected. Therefore, it is recommended to run the characterization experiment script in a persistent shell session (e.g., using a terminal multiplexer like screen, tmux).

### Step 1 

Clone the repo in home directory

```
  $ git clone https://github.com/CMU-SAFARI/SiMRA-DRAM/
```

Go to the program folder
```
  $ cd /home/<your_user_name>/dsn_artifact/DRAM-Bender/sources/apps/DSN_AE_APPS/
```
### Step 2 

Run `run_all_scripts.py` to perform all characterization experiments. We expect this to take approximately more than a week. When the script successfully finishes, all reproduced characterization data gets copied to `experimental_data/new_data_tested_module` directory.
```
  $ python3 run_all_scripts.py
```
After all experiments are done, you will see the following output:
```
  #############################################                        
  All experiments are done!                                                                 
  #############################################   
```
### Step 3

Reproducing figures from existing characterization data. All experimental data presented in the paper is in our Zenodo repository. Extract dsn_artifact.zip and move the experimental_data directory to this repo's experimental_data directory.

Use `analysis/plot_all_results.py` Python script to reproduce figures with existing characterization results with newly-generated characterization results.

### Elobarating on Experiments

In this study, we conduct four main experiments.
 - Reverse-engineering subarray boundaries using the RowClone operation. 
 - Evaluating the reliability of activating multiple rows in off-the-shelf DRAM chips.
 - Evaluating the in-DRAM three-input, five-input, seven-input, and nine-input majority operations (i.e., MAJ3, MAJ5, MAJ7, and MAJ9).
 - Evaluating the in-DRAM copy operations where one row's content is copied to 1, 3, 7, 15, and 31 rows (i.e., MultiRowCopy).

 The main script (`run_all_scripts.py`) conduct all the experiments sequentially.

 #### 1. Reverse-engineering Subarray Boundaries

 In this experiment, we test all rows in a DRAM module to uncover the subarray boundaries and which rows are in which subarrays. The main script `run_all_scripts.py` 1) compiles the DRAM-Bender program (i.e., `DRAM-Bender/sources/apps/DSN_AE_APPS/RowClone/test.cpp`) and 2) run the python script that calls the DRAM-Bender program (i.e., `DRAM-Bender/sources/apps/DSN_AE_APPS/RowClone/run_script.py`), covering all the DRAM rows. 
 
 The output of this experiment is `all_subarrays.csv`, which will be used as an input in the second experiment. The output can be found in `experimental_data/<your_tested_module_name>` and `DRAM-Bender/sources/apps/DSN_AE_APPS/RowClone/` directories.

 #### 2. Evaluating the Reliability of Simultaneously Activating Multiple Rows 

 In this experiment, we randomly choose three subarrays and issue ACT RowX - PRE - ACT RowY command sequence with violated timings where RowX and RowY are in the same subarray and RowX < RowY. The main script `run_all_scripts.py` 1) compiles the DRAM-Bender program (i.e., `DRAM-Bender/sources/apps/DSN_AE_APPS/FindOpenRows/test_find_open_rows.cpp`) and 2) run the python script that calls the DRAM-Bender program (i.e., `DRAM-Bender/sources/apps/DSN_AE_APPS/FindOpenRows/run_script.py`) with sweeping operating parameters (e.g., timing delays). 

 The outputs of this experiment are `open_rows_50.csv` and `random_subarrays_list.csv`, where we have the reliability of simultaneously activating multiple rows and chosen random subarrays, respectively. The output can be found in `experimental_data/<your_tested_module_name>` and `DRAM-Bender/sources/apps/DSN_AE_APPS/FindOpenRows/` directories.

 #### 3. Evaluating the Reliability of in-DRAM Majority Operations

 In this experiment, we randomly choose 100 row groups that are simultaneously activated from each three randomly chosen subarrays.  The main script `run_all_scripts.py` 1) compiles the DRAM-Bender program (i.e., `DRAM-Bender/sources/apps/DSN_AE_APPS/MajOperations/test.cpp`) and 2) run the python script that calls the DRAM-Bender program (i.e., `DRAM-Bender/sources/apps/DSN_AE_APPS/FindOpenRows/run_script.py`) with sweeping operating parameters (e.g., data pattern). 

 The outputs of this experiments are 1) `maj_coverage_4_50.csv`, `maj_coverage_8_50.csv` , `maj_coverage_16_50.csv` and `maj_coverage_32_50.csv` which stores the reliability of MAJ operations and 2) `samples_4.csv`, `samples_8.csv`, `samples_16.csv` and `samples_32.csv` which stores the randomly chosen 100 row groups from each subarray. The output can be found in `experimental_data/<your_tested_module_name>`.

  #### 4. Evaluating the Reliability of in-DRAM Copy Operations

  In this experiment, we use chosen 100 row groups that are simultaneously activated from each three randomly chosen subarrays.  The main script `run_all_scripts.py` 1) compiles the DRAM-Bender program (i.e., `DRAM-Bender/sources/apps/DSN_AE_APPS/MultiRowInit/test.cpp`) and 2) run the python script that calls the DRAM-Bender program (i.e., `DRAM-Bender/sources/apps/DSN_AE_APPS/MultiRowInit/run_script.py`) with sweeping operating parameters (e.g., timing delays). 

  The outputs of this experiments are 1) `multirow_2_50.csv`, `multirow_4_50.csv`, `multirow_8_50.csv`, `multirow_16_50.csv`, and `multirow_32_50.csv` that stores the reliability of in-DRAM copy operations and 2) `samples_4.csv` that has the chosen row groups for simultaneously activating two rows. The output can be found in `experimental_data/<your_tested_module_name>`.

## Contact:
Ismail Emir Yuksel (ismail.yuksel [at] safari [dot] ethz [dot] ch)  

