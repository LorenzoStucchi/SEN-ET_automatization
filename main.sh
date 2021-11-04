#!/bin/bash

python py_scripts/1_create_script_graph.py
sh output/1_script_gpt_s3.sh
python py_scripts/2_read_times_s3.py
sh output/2_script_gpt_s2.sh
python py_scripts/3_create_script_python.py
sh output/3_script_S2.sh
sh output/4_script_S3.sh
read -r -p "Computation ended sucessfully! Press any key to close the panel" input