#!/bin/bash

python3 py_scripts/0_path_read.py
echo "==================="
python3 py_scripts/1_create_script_graph.py
echo "==================="
sh output/0_script_download_era.sh
echo "==================="
sh output/1_script_gpt_s3.sh
echo "==================="
python3 py_scripts/2_read_times_s3.py
echo "==================="
sh output/2_script_gpt_s2.sh
echo "==================="
python3 py_scripts/3_create_script_python.py
echo "==================="
sh output/3_script_S2.sh
echo "==================="
sh output/4_script_S3.sh
#read -r -p "Computation ended sucessfully! Press any key to close the panel" input