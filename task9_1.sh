#!/bin/bash
#BSUB -J task9_1
#BSUB -q c02613
#BSUB -gpu "num=1:mode=exclusive_process"
#BSUB -W 00:30
#BSUB -R "rusage[mem=512MB]"
#BSUB -o task9_%J.out
#BSUB -e task9_%J.err

#BSUB -n 4

#BSUB -R "span[hosts=1]"

#BSUB -R "select[model==XeonGold6226R]"

# Intialize python environment
source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

time python simulate_cupy.py
time python simulate_cupy.py 5
time python simulate_cupy.py 10
time python simulate_cupy.py 15
time python simulate_cupy.py 20
