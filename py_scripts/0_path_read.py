import os
import json
import datetime

def is_valid_date(input_date):
    try:
        date = input_date.split("_")
        newDate = datetime.datetime(int(date[0]),int(date[1]),int(date[2]))
        return True
    except ValueError:
        return False

path_param = "input\\parameters.json"

with open(path_param, "r") as f:
    param = json.load(f)

general_path = param["general_path"]

sub_folders = [name for name in os.listdir(general_path) if os.path.isdir(os.path.join(general_path, name))]

for folder in sub_folders:
    temp_path = general_path + "\\" + folder
    if folder == "S2":
        list_s2_days = [temp_path + "\\" + name for name in os.listdir(temp_path) if os.path.isdir(os.path.join(temp_path, name))]
        valid_s2_days = [day for day in list_s2_days if is_valid_date(day.split("\\")[-1])]
        list_s2_images = [[path + "\\" + name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))] for path in valid_s2_days]
        list_s2_images = [item for sublist in list_s2_images for item in sublist]
        valid_list_s2_images = [imm for imm in list_s2_images if imm[-5:] == ".SAFE"]
    elif folder ==  "S3":
        list_s3_days = [temp_path + "\\" + name for name in os.listdir(temp_path) if os.path.isdir(os.path.join(temp_path, name))]
        valid_s3_days = [day for day in list_s3_days if is_valid_date(day.split("\\")[-1])]
        list_s3_images = [[path + "\\" + name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))] for path in valid_s3_days]
        list_s3_images = [item for sublist in list_s3_images for item in sublist]
        valid_list_s3_images = [imm for imm in list_s3_images if imm[-5:] == ".SEN3"]

s2_paths = "input/s2_paths.txt"
f_s2_paths = open(s2_paths, "w")
for element in valid_list_s2_images:
    f_s2_paths.write(element + "\n")
f_s2_paths.close()

s3_paths = "input/s3_paths.txt"
f_s3_paths = open(s3_paths, "w")
for element in valid_list_s3_images:
    f_s3_paths.write(element + "\n")
f_s3_paths.close()

print("\tPath files created!\n\t" + s2_paths + "\n\t" + s3_paths)