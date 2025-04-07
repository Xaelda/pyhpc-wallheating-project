#!/bin/bash
#BSUB -J Task_8_2_GPU             # Job name
#BSUB -o Task_8_2_GPU_output%J.txt       # Standard output file
#BSUB -e Task_8_2_GPU_error%J.txt        # Standard error file
#BSUB -q gpuv100                   # Use the default HPC queue
#BSUB -W 00:30                    # Wall time limit (2 minutes)
#BSUB -gpu "num=2:mode=exclusive_process"          # Request 1 GPU

#BSUB -n 8                # Request 1 CPU cores
#BSUB -R "span[hosts=1]"           # Request all cores on the same host
#BSUB -R "rusage[mem=16GB]"


source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

time python -u Task_8.py