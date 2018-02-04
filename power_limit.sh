#!/bin/bash

echo "Run as sudo to lower power-limits."
echo ""

power=${1:-30}



# 250w 1080ti sc2
nvidia-smi -i 0 -pl $((250-power)) 
# 180w 1070ti
nvidia-smi -i 1 -pl $((160-power)) 
# 180w 1070ti
nvidia-smi -i 2 -pl $((160-power)) 
# 280w 1080ti ftw
nvidia-smi -i 3 -pl $((260-power)) 
# 150w 1070 founder
nvidia-smi -i 4 -pl $((150-power)) 
# 250w 1080ti sc2
nvidia-smi -i 5 -pl $((250-power)) 

echo ""
echo ""

nvidia-smi
