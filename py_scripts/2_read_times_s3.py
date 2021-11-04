import xarray as xr
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
    path = general_path + "S3\\"  + day + "\\S3_" + day + "_time.nc"
    ds = xr.open_dataset(path)
    start_time = int(ds.attrs["start_date"][12:14])*60 + int(ds.attrs["start_date"][15:17])
    end_time = int(ds.attrs["stop_date"][12:14])*60 + int(ds.attrs["stop_date"][15:17])
    mean_time = int((start_time + end_time)/2)
    mean_time_h = int(mean_time/60)
    mean_time_m = int(mean_time%60)
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