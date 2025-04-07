#!/bin/bash
#BSUB -J task_7_3
#BSUB -q hpc
#BSUB -W 00:20
#BSUB -R "rusage[mem=4GB]"
#BSUB -o task_7_3_%J.out
#BSUB -e task_7_3_%J.err

#BSUB -n 1

#BSUB -R "span[hosts=1]"

#BSUB -R "select[model==XeonGold6226R]"

# Intialize python environment
source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

time python simulate_JIT.py 1
time python simulate_JIT.py 100
