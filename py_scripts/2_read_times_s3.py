import xml.etree.ElementTree as ET
import json

path_param = "input\\parameters.json"
path_file_date_s3 = "output\\days_s3.txt"
path_file_datetime_s3 = "output\\days_time_s3.txt"

# Definition of general varibles
with open(path_param, "r") as f:
    p = json.load(f)
general_path = p["general_path"]

# Variable for Sentinel 3 images
file_date_s3 = open(path_file_date_s3, "r")
date_s3 = []
for line in file_date_s3:
    date = line.strip()
    date_s3.append(date)
file_date_s3.close()

text = ""
for day in date_s3:
    path = general_path + "S3\\"  + day + "\\S3_" + day + "_mask.dim"
    for line in open(path, 'r').readlines():
        if "PRODUCT_SCENE_RASTER_START_TIME" in line:
            data_start = line.split(">")[1].split("<")[0]
        if "PRODUCT_SCENE_RASTER_STOP_TIME" in line:
            data_end = line.split(">")[1].split("<")[0]
    start_time = int(data_start[12:14])*3600 + int(data_start[15:17])*60 + float(data_start[18:])
    end_time = int(data_end[12:14])*3600 + int(data_end[15:17])*60 + float(data_start[18:])
    mean_time = float((start_time + end_time)/2)
    mean_time_h = int(mean_time/3600)
    mean_time_m = int(mean_time%3600/60)
    if mean_time_h < 10:
        hours = "0" + str(mean_time_h)
    else:
        hours = str(mean_time_h)
    if mean_time_m < 10:
        minutes = "0" + str(mean_time_m)
    else:
        minutes = str(mean_time_m)
    text = text + day + " " + hours + ":" + minutes + "\n"

f = open(path_file_datetime_s3, "w")
f.write(text)
f.close()

print("\tTimes file created!\n\t" + path_file_datetime_s3)