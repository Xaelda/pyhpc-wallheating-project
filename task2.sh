#!/bin/bash
#BSUB -J task2
#BSUB -q hpc
#BSUB -W 00:05
#BSUB -R "rusage[mem=512MB]"
#BSUB -o task2_%J.out
#BSUB -e task2_%J.err

#BSUB -n 15

#BSUB -R "span[hosts=1]"

#BSUB -R "select[model==XeonGold6226R]"

# Intialize python environment
source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

time python simulate.py 10


