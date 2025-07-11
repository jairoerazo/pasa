#!/bin/bash
#SBATCH --job-name=pasa     
#SBATCH --output=run/pasa_product_1.out
#SBATCH --error=run/pasa_product_1.err
#SBATCH --time=8:00:00             
#SBATCH --partition=gpu          
#SBATCH --ntasks=1                   
#SBATCH --cpus-per-task=4            
#SBATCH --mem=64G                     
#SBATCH --gpus=h100:1

module load CUDA/11.8.0
source $(conda info --base)/etc/profile.d/conda.sh
conda activate msgai-project
python run_product_agent.py
