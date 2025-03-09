#!/bin/bash
#BSUB -J task_5
#BSUB -q hpc
#BSUB -W 00:20
#BSUB -R "rusage[mem=4GB]"
#BSUB -o task_5_%J.out
#BSUB -e task_5_%J.err

#BSUB -n 16

#BSUB -R "span[hosts=1]"

#BSUB -R "select[model==XeonGold6226R]"

# Intialize python environment
source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

time python simulate_w_parallel.py 20 1
time python simulate_w_parallel.py 20 2
time python simulate_w_parallel.py 20 4
time python simulate_w_parallel.py 20 8
time python simulate_w_parallel.py 20 16