#!/bin/bash
#BSUB -J task_4
#BSUB -q hpc
#BSUB -W 00:10
#BSUB -R "rusage[mem=4GB]"
#BSUB -o task_4_%J.out
#BSUB -e task_4_%J.err

#BSUB -n 1

#BSUB -R "span[hosts=1]"

#BSUB -R "select[model==XeonGold6226R]"

# Intialize python environment
source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

kernprof -l simulate.py 20
python -m line_profiler -rmt "simulate.py.lprof"