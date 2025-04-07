#!/bin/bash
#BSUB -J task_7_1_1
#BSUB -q hpc
#BSUB -W 00:40
#BSUB -R "rusage[mem=4GB]"
#BSUB -o task_7_1_1_%J.out
#BSUB -e task_7_1_1_%J.err

#BSUB -n 1

#BSUB -R "span[hosts=1]"

#BSUB -R "select[model==XeonGold6226R]"

# Intialize python environment
source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

time python simulate_JIT.py 50
time python simulate.py 50
