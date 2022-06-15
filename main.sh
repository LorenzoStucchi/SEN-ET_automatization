#!/bin/bash

time python3 py_scripts/0_path_read.py
echo "==================="
time python3 py_scripts/1_create_script_graph.py
echo "==================="
time sh output/1_script_gpt_s3.sh
echo "==================="
time python3 py_scripts/2_read_times_s3.py
echo "==================="
time sh output/2_script_gpt_s2.sh
echo "==================="
time python3 py_scripts/3.py
echo "==================="
time sh output/3_script_S2.sh
echo "==================="
time sh output/4_script_S3.sh
#read -r -p "Computation ended sucessfully! Press any key to close the panel" input