import xml.etree.ElementTree as ET
import json

file_param = "input/parameters.json"
file_path = "output/path.json"
path_file_datetime = "output/path_hour.json"

# Definition of general varibles
with open(file_param, "r") as f:
    p = json.load(f)

with open(file_path, "r") as f:
    images = json.load(f)["data"]

for image in images:
    try:
        if image["platform"] == "S3":
            path = image["derived_product_path"] + "/S3_mask.dim"
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
            image["hour"] = hours + ":" + minutes

        if image["uid"] == 0 :
            temp = "\t\t" + str(image).replace("\'","\"").replace(", ", ",\n\t\t\t").replace("{", "{\n\t\t\t").replace("}","\n\t\t}")
        else: 
            temp = temp + ",\n\t\t" + str(image).replace("\'","\"").replace(", ", ",\n\t\t\t").replace("{", "{\n\t\t\t").replace("}","\n\t\t}")
    except:
        print("Error with images, not possible to open it" + str(image["derived_product_path"]) )

j = "{\n\t\"data\":\n\t[\n" + temp + "\n\t]\n}"
with open(path_file_datetime, "w") as f:
    f.write(j)

print("\tTimes file created!\n\t" + path_file_datetime)