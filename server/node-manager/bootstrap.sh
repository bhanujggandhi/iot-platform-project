#!/bin/zsh

echo "STARTING THE PLATFORM"

# Load modules array from YAML config
mdls=("internal-api" "notification" "monitoring")

# Loop through modules and apply manifests
for module in "${mdls[@]}";
do
    echo "Applying manifests for module: $module"   
    kubectl delete -f ./"$module"/manifests
done

echo "STARTING THE NODE MANAGER"
python main.py
