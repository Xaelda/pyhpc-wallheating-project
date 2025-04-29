#!/bin/bash
#BSUB -J task9_2
#BSUB -q c02613
#BSUB -gpu "num=1:mode=exclusive_process"
#BSUB -W 00:30
#BSUB -R "rusage[mem=512MB]"
#BSUB -o task9_2_%J.out
#BSUB -e task9_2_%J.err

#BSUB -n 4

#BSUB -R "span[hosts=1]"

#BSUB -R "select[model==XeonGold6226R]"

# Intialize python environment
source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

nsys profile -o profile_9_2 python simulate_cupy.py 20
