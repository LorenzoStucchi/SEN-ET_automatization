import json
import os
import math

path_param = "input/parameters.json"
path_file_path = "output/path.json"
path_graph_s2_pro = "graph/sentinel_2_pre_processing.xml"
path_graph_LC = "graph/add_landcover.xml"
path_graph_ele = "graph/add_elevation.xml"
path_graph_s3_pro = "graph/sentinel_3_pre_processing.xml"
path_script_s3 = "output/1_script_gpt_s3.sh"
path_script_s2 = "output/2_script_gpt_s2.sh"

# Definition of general varibles
with open(path_param, "r") as f:
    param = json.load(f)
intermediate_output_path = param["temp_files"]
with open(path_file_path, "r") as f:
    images = json.load(f)["data"]

# Save xml files to variable
f = open(path_graph_s2_pro, "r")
graph_s2_pro = f.read()
f.close()
f = open(path_graph_LC, "r")
graph_LC = f.read()
f.close()
f = open(path_graph_ele, "r")
graph_ele = f.read()
f.close()
f = open(path_graph_s3_pro, "r")
graph_s3_pro = f.read()
f.close()

script_text_s3 = ""
script_text_s2 = ""

for image in images:
    path_derived = image["derived_product_path"]  + "/graph"
    if os.path.isdir(path_derived) == False:
        os.makedirs(path_derived)
    if image["platform"] == "S2":
        try:
            n = max(n, math.ceil(float(image["bbox"]["n"])))
            s = min(s, math.floor(float(image["bbox"]["s"])))
            e = max(e, math.ceil(float(image["bbox"]["e"])))
            w = min(w, math.floor(float(image["bbox"]["w"])))
        except NameError:
            n = math.ceil(float(image["bbox"]["n"]))
            s = math.floor(float(image["bbox"]["s"]))
            e = math.ceil(float(image["bbox"]["e"]))
            w = math.floor(float(image["bbox"]["w"]))

AOI_WTK = "POLYGON ((" + str(w) + " " + str(n) + ", " + str(e) + " " + str(n) + ", " + str(e) + " " + str(s) + ", " + str(w) + " " + str(s) + ", " + str(w) + " " + str(n) + ", " + str(w) + " " + str(n) + "))"

i = 1
j = 1

for image in images:
    # Creation of script and xml file for S3
    if image["platform"] == "S3":
        id_s3 = image["tile"]
        date = image["day"]
        path = image["derived_product_path"]

        # Processing
        script_text_s3 = script_text_s3 + "echo \"\tPRE-S3 " + str(i) + "/TOTALITERATION Processing the image S3 " + date + "_" + id_s3 + "\"\n"
        obs_image = path + "/S3_obs_geometry.dim"
        mask_image = path + "/S3_mask.dim"
        lst_image = path + "/S3_lst.dim"
        text_s3_pro = graph_s3_pro.replace("!INPUT_Sentinel-3_LST!", image["path"]).replace("!INPUT_AOI_WKT!", AOI_WTK).replace("!OUTPUT_observation_geometry!", obs_image).replace("!OUTPUT_mask!", mask_image).replace("!OUTPUT_LST!", lst_image)
        path_s3_pro = path + "/graph/" + "sentinel_3_preprocessing_"  + date + "_" + id_s3 +".xml"
        script_text_s3 = script_text_s3 + "time gpt " + path_s3_pro + "\n" + "\n\n"
        f = open(path_s3_pro, "w")
        f.write(text_s3_pro)
        f.close()

        i = i + 1

    # Creation of script and xml file for S2
    elif image["platform"] == "S2":
        tile = image["tile"]
        date = image["day"]
        path = image["derived_product_path"]
        sensor_s2 = " ".join(image["path"].split("/")[-2:])[:3]
        
        # Processing
        script_text_s2 = script_text_s2 + "echo \"\tPRE-S2 " + str(j) + "/TOTALITERATION Processing the image S2 " + date + "_" + tile + "\"\n"
        mask_image = path + "/S2_mask.dim"
        bio_image = path + "/S2_biophysical.dim"
        refl_image = path + "/S2_reflectance.dim"
        resample_image = path + "/S2_resampled.dim"
        zen_image = path + "/S2_sun_zenith_angle.dim"
        text_s2_pro = graph_s2_pro.replace("!INPUT_Sentinel-2_L2A!", image["path"]).replace("!OUTPUT_mask!", mask_image).replace("!OUTPUT_biophysical!", bio_image).replace("!INPUT_Sensor_S2!", sensor_s2).replace("!OUTPUT_reflectance!", refl_image).replace("!OUTPUT_resampled!", resample_image).replace("!OUTPUT_sun_zenith_angle!", zen_image)
        path_s2_pro = path + "/graph/" + "sentinel_2_pre_processing_"  + date + "_" + tile +".xml"
        script_text_s2 = script_text_s2 + "time gpt " + path_s2_pro + "\n"
        f = open(path_s2_pro, "w")
        f.write(text_s2_pro)
        f.close()
        
        # Landcover
        script_text_s2 = script_text_s2 + "echo \"\tPRE-S2 " + str(j+1) + "/TOTALITERATION Computing the landcover for the image S2 " + date + "\"\n"
        LC_image = path + "/S2_landcover.dim"
        text_LC = graph_LC.replace("!INPUT_Sentinel-2_Mask!", mask_image).replace("!OUTPUT_CCI_landcover!", LC_image)
        path_LC = path + "/graph/" + "add_landcover_"  + date + "_" + tile +".xml"
        script_text_s2 = script_text_s2 + "time gpt " + path_LC + "\n"
        script_text_s2 = script_text_s2 + "echo \"Computed the landcover for the image S2 " + date + "_" + tile + "\"\n"
        f = open(path_LC, "w")
        f.write(text_LC)
        f.close()

        # Elevation
        script_text_s2 = script_text_s2 + "echo \"\tPRE-S2 " + str(j+2) + "/TOTALITERATION Computing the elevation for the image S2 " + date + "_" + tile + "\"\n"
        ele_image = path + "/S2_elevation.dim"
        text_ele = graph_ele.replace("!INPUT_Sentinel-2_Mask!", mask_image).replace("!OUTPUT_SRTM_elevation!", ele_image)
        path_ele = path + "/graph/" + "add_elevation_"  + date + "_" + tile +".xml"
        script_text_s2 = script_text_s2 + "time gpt " + path_ele + "\n" 
        script_text_s2 = script_text_s2 + "echo \"Computed the elevation for the image S2 " + date + "\"\n" + "\n\n"
        f = open(path_ele, "w")
        f.write(text_ele)
        f.close()

        j = j + 1

script_text_s2 = script_text_s2.replace("TOTALITERATION", str(j-1))
script_text_s3 = script_text_s3.replace("TOTALITERATION", str(i-1))

f = open(path_script_s3, "w")
f.write(script_text_s3)
f.close()
f = open(path_script_s2, "w")
f.write(script_text_s2)
f.close()

print("\tScripts created!\n\t" + path_script_s3 + "\n\t" + path_script_s2)