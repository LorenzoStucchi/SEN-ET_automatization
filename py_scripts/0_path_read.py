import os
import json

path_images_file = "input/images.txt"
path_param = "input/parameters.json"

n = 0
s2_text = ""
s3_text = ""
s_json_template = "\t\t{ \n\t\t\t\"uid\": UID, \n\t\t\t\"platform\": \"PLATFORM\", \n\t\t\t\"path\": \"PATH\", \n\t\t\t\"derived_product_path\": \"INTERMEDIATE\", \n\t\t\t\"tile\": \"TILEID\", \n\t\t\t\"time\": \"TIME\" \n\t\t}"

images_file = open(path_images_file, "r")

with open(path_param, "r") as f:
    intermediate_output_path = json.load(f)["temp_files"]

# Create directory
if os.path.isdir("output") == False:
    os.mkdir("output")

for line in images_file:
    components = line.split("_")
    sentinel = components[0]
    if sentinel == "S2A" or sentinel == "S2B":
        sensor = components[1][0:3]
        level = components[1][3:6]
        date = components[2]
        year = date[0:4]
        month = date[4:6]
        day = date[6:8]
        if ".SAFE" in line:
            name = line.strip()
        else:
            name = line.strip() + ".SAFE"
        if level == "L2A":
            tile = name.split("_")[5]
            if s2_text == "":
                s2_text = s_json_template.replace("UID", str(n)).replace("PLATFORM", "S2").replace("PATH", "/eodata/Sentinel-2/" + sensor + "/" + level + "/" + year + "/" + month + "/" + day + "/" + name + "/MTD_MSIL2A.xml").replace("TILEID", tile).replace("TIME", year + "_" + month + "_" + day).replace("INTERMEDIATE", intermediate_output_path + "/"  + tile + "/" + year + "/" + month + "/" + day )
            else:
                s2_text = s2_text + ",\n" + s_json_template.replace("UID", str(n)).replace("PLATFORM", "S2").replace("PATH", "/eodata/Sentinel-2/" + sensor + "/" + level + "/" + year + "/" + month + "/" + day + "/" + name + "/MTD_MSIL2A.xml").replace("TILEID", tile).replace("TIME", year + "_" + month + "_" + day).replace("INTERMEDIATE", intermediate_output_path + "/"  + tile + "/" + year + "/" + month + "/" + day)
            n = n + 1
        else:
            print(name + "is not a valid Sentinel-2 L2A image")
    elif sentinel == "S3A" or sentinel == "S3B":
        level = components[2]
        sensor = components[3]
        date = components[7]
        year = date[0:4]
        month = date[4:6]
        day = date[6:8]
        if ".SEN3" in line:
            name = line.strip()
        else:
            name = line.strip() + ".SEN3"
        if sensor == "LST" and level == "2":
            tile = name[64:81]
            if s3_text == "":
                s3_text = s_json_template.replace("UID", str(n)).replace("PLATFORM", "S3").replace("PATH", "/eodata/Sentinel-3/SLSTR/SL_2_LST/" + year + "/" + month + "/" + day + "/" + name + "/xfdumanifest.xml").replace("TILEID", tile).replace("TIME", year + "_" + month + "_" + day).replace("INTERMEDIATE", intermediate_output_path + "/"  + tile + "/" + year + "/" + month + "/" + day)
            else:
                s3_text = s3_text + ",\n" + s_json_template.replace("UID", str(n)).replace("PLATFORM", "S3").replace("PATH", "/eodata/Sentinel-3/SLSTR/SL_2_LST/" + year + "/" + month + "/" + day + "/" + name + "/xfdumanifest.xml").replace("TILEID", tile).replace("TIME", year + "_" + month + "_" + day).replace("INTERMEDIATE", intermediate_output_path + "/"  + tile + "/" + year + "/" + month + "/" + day)
            n = n + 1
        else:
            print(name + "is not a valid Sentinel-3 LST image")

images_file.close()

if s2_text == "":
    print("ERROR: no Sentinel 2 images found")
elif s3_text == "":
    print("ERROR: no Sentinel 3 images found")    
else:
    j = "{\n\t\"data\":\n\t[\n" + s2_text + ",\n" + s3_text + "\n\t]\n}"
    with open("output/path.json", "w") as f:
        f.write(j)

print("\tPath file created!\n\t output/path.json\n\t")