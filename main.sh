#!/bin/bash

python 1_create_script_graph.py
sh output/1_script_gpt_s3.sh
echo "===================================================================="
echo "===================================================================="
echo "Open SNAP and set the hour of s3 images in the file days_time_s3.txt"
echo "===================================================================="
echo "===================================================================="
sleep 30
sh output/2_script_gpt_s2.sh
read -r -p "Do you set the S3 time in the file days_time_s3.txt? [Y/n] " input
if [[ $input == Y ]] || [[ $input == y ]]
then
    python 2_create_script_python.py
    sh output/3_script_S2.sh
    sh output/4_script_S3.sh
    echo "Computation ended sucessfully"
else
    read -r -p "Please, set the hour and minute of the Sentinel 3 images in the file days_time_s3.txt and then press Y: " input
    if [[ $input == Y ]] || [[ $input == y ]]
    then
        python 2_create_script_python.py
        sh output/3_script_S2.sh
        sh output/4_script_S3.sh
        echo "Computation ended sucessfully"
    else
        echo "Wrong value chose, the script will end without computation"
    fi
fi