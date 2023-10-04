import os
import json
path_param = "input\\parameters.json"
path_file_path_s2 = "input\\s2_paths.txt"
path_file_path_s3 = "input\\s3_paths.txt"
path_s2_pro = "graph\\sentinel_2_pre_processing.xml"
path_LC = "graph\\add_landcover.xml"
path_ele = "graph\\add_elevation.xml"
path_s3_pro = "graph\\sentinel_3_pre_processing.xml"
path_graph = "output\\graph\\"
path_date_s2 = "output\\days_s2.txt"
path_date_s3 = "output\\days_s3.txt"
path_script_s3 = "output\\1_script_gpt_s3.sh"
path_script_s2 = "output\\2_script_gpt_s2.sh"

# Create directory
if os.path.isdir("output") == False:
    os.mkdir("output")
    os.mkdir("output\graph")
else:
    if os.path.isdir("output\graph") == False:
        os.mkdir("output\graph")

# Definition of general varibles
with open(path_param, "r") as f:
    param = json.load(f)
AOI_WTK = "POLYGON ((" + str(param["AOI"]["west"]) + " " + str(param["AOI"]["north"]) + ", " + str(param["AOI"]["est"]) + " " + str(param["AOI"]["north"]) + ", " + str(param["AOI"]["est"]) + " " + str(param["AOI"]["south"]) + ", " + str(param["AOI"]["west"]) + " " + str(param["AOI"]["south"]) + ", " + str(param["AOI"]["west"]) + " " + str(param["AOI"]["north"]) + ", " + str(param["AOI"]["west"]) + " " + str(param["AOI"]["north"]) + "))"
general_path = param["general_path"]

# Save xml files to variable
f = open(path_s2_pro, "r")
graph_s2_pro = f.read()
f.close()
f = open(path_LC, "r")
graph_LC = f.read()
f.close()
f = open(path_ele, "r")
graph_ele = f.read()
f.close()
f = open(path_s3_pro, "r")
graph_s3_pro = f.read()
f.close()

# Creatin of script and xml file for S3
file_path_s3 = open(path_file_path_s3, "r")
script_text = ""
date_s3 = ""
for line in file_path_s3:
    s3_image_path = line.strip()
    path = "\\".join(s3_image_path.split("\\")[:-1])
    date = " ".join(s3_image_path.split("\\")[-2:-1])
    date_s3 = date_s3 + date + "\n"
    
    s3_image_path = s3_image_path + "\\xfdumanifest.xml"
    
    # Processing
    script_text = script_text + "echo \"\t Processing the image S3 " + date + "\"\n"
    obs_image = path + "\\S3_" + date + "_obs_geometry.dim"
    mask_image = path + "\\S3_" + date + "_mask.dim"
    lst_image = path + "\\S3_" + date + "_lst.dim"
    text_s3_pro = graph_s3_pro.replace("!INPUT_Sentinel-3_LST!", s3_image_path).replace("!INPUT_AOI_WKT!", AOI_WTK).replace("!OUTPUT_observation_geometry!", obs_image).replace("!OUTPUT_mask!", mask_image).replace("!OUTPUT_LST!", lst_image)
    path_s3_pro = path_graph + "sentinel_3_preprocessing_"  + date +".xml"
    script_text = script_text + "gpt " + path_s3_pro + "\n" + "\n\n"
    f = open(path_s3_pro, "w")
    f.write(text_s3_pro)
    f.close()
file_path_s3.close()

script_text = script_text.replace("\\", "\\\\")

f = open(path_date_s3, "w")
f.write(date_s3)
f.close()
f = open(path_script_s3, "w")
f.write(script_text)
f.close()

# Creatin of script and xml file for S2
file_path_s2 = open(path_file_path_s2, "r")
script_text = ""
date_s2 = ""
for line in file_path_s2:
    s2_image_path = line.strip()
    path = "\\".join(s2_image_path.split("\\")[:-1])
    date = " ".join(s2_image_path.split("\\")[-2:-1])
    date_s2 = date_s2 + date + "\n"
    
    sensor_s2 = " ".join(s2_image_path.split("\\")[-1:])[:3]
    s2_image_path = s2_image_path + "\\MTD_MSIL2A.xml"

    # Processing
    script_text = script_text + "echo \"\t Processing the image S2 " + date + "\"\n"
    mask_image = path + "\\S2_" + date + "_mask.dim"
    bio_image = path + "\\S2_" + date + "_biophysical.dim"
    refl_image = path + "\\S2_" + date + "_reflectance.dim"
    resample_image = path + "\\S2_" + date + "_resampled.dim"
    zen_image = path + "\\S2_" + date + "_sun_zenith_angle.dim"
    text_s2_pro = graph_s2_pro.replace("!INPUT_Sentinel-2_L2A!", s2_image_path).replace("!OUTPUT_mask!", mask_image).replace("!OUTPUT_biophysical!", bio_image).replace("!INPUT_Sensor_S2!", sensor_s2).replace("!OUTPUT_reflectance!", refl_image).replace("!OUTPUT_resampled!", resample_image).replace("!OUTPUT_sun_zenith_angle!", zen_image)
    path_s2_pro = path_graph + "sentinel_2_pre_processing_"  + date +".xml"
    script_text = script_text + "gpt " + path_s2_pro + "\n"
    f = open(path_s2_pro, "w")
    f.write(text_s2_pro)
    f.close()
    
    # Landcover
    script_text = script_text + "echo \"\t Computing the landcover for the image S2 " + date + "\"\n"
    LC_image = path + "\\S2_" + date + "_landcover.dim"
    text_LC = graph_LC.replace("!INPUT_Sentinel-2_Mask!", mask_image).replace("!OUTPUT_CCI_landcover!", LC_image)
    path_LC = path_graph + "add_landcover_"  + date +".xml"
    script_text = script_text + "gpt " + path_LC + "\n"
    f = open(path_LC, "w")
    f.write(text_LC)
    f.close()

    # Elevation
    script_text = script_text + "echo \"\t Computing the elevation for the image S2 " + date + "\"\n"
    ele_image = path + "\\S2_" + date + "_elevation.dim"
    text_ele = graph_ele.replace("!INPUT_Sentinel-2_Mask!", mask_image).replace("!OUTPUT_SRTM_elevation!", ele_image)
    path_ele = path_graph + "add_elevation_"  + date +".xml"
    script_text = script_text + "gpt " + path_ele + "\n" +"\n\n"
    f = open(path_ele, "w")
    f.write(text_ele)
    f.close()
file_path_s2.close()

script_text = script_text.replace("\\", "\\\\")

# Save file date and scirpt
f = open(path_date_s2, "w")
f.write(date_s2)
f.close()
f = open(path_script_s2, "w")
f.write(script_text)
f.close()

print("\tScripts created!\n\t" + path_script_s3 + "\n\t" + path_script_s2)