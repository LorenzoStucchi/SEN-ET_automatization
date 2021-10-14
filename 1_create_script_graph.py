import os
import json
path_param = "input\\parameters.json"
path_file_path_s2 = "input\\s2_path.txt"
path_file_path_s3 = "input\\s3_path.txt"
path_bandmask = "graph\\BandMaths_mask_sentinel_2_pre_processing.xml"
path_bio = "graph\\BiophysicalOp_sentinel_2_pre_processing.xml"
path_refl = "graph\\reflectance_sentinel_2_pre_processing.xml"
path_resample = "graph\\resample_sentinel_2_pre_processing.xml"
path_zen = "graph\\sun_zenith_sentinel_2_pre_processing.xml"
path_LC = "graph\\add_landcover.xml"
path_ele = "graph\\add_elevation.xml"
path_cut = "graph\\sentinel_3_cut.xml"
path_s3_pro = "graph\\sentinel_3_pre_processing_fix.xml"
path_graph = "output\\graph\\"
path_date_s2 = "output\\days_s2.txt"
path_date_s3 = "output\\days_ADDTIME_s3.txt"
path_script = "output\\1_script_gpt.sh"

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
# AOI_WTK = "POLYGON ((" + param[5] + " " + param[1] + ", " + param[7] + " " + param[1] + ", " + param[7] + " " + param[3] + ", " + param[5] + " " + param[3] + ", " + param[5] + " " + param[1] + ", " + param[5] + " " + param[1] + "))"
AOI_WTK = "POLYGON ((" + str(param["AOI"]["west"]) + " " + str(param["AOI"]["north"]) + ", " + str(param["AOI"]["est"]) + " " + str(param["AOI"]["north"]) + ", " + str(param["AOI"]["est"]) + " " + str(param["AOI"]["south"]) + ", " + str(param["AOI"]["west"]) + " " + str(param["AOI"]["south"]) + ", " + str(param["AOI"]["west"]) + " " + str(param["AOI"]["north"]) + ", " + str(param["AOI"]["west"]) + " " + str(param["AOI"]["north"]) + "))"
general_path = param["general_path"]

# Save xml files to variable
f = open(path_bandmask, "r")
graph_bandmask = f.read()
f.close()
f = open(path_bio, "r")
graph_bio = f.read()
f.close()
f = open(path_refl, "r")
graph_refl = f.read()
f.close()
f = open(path_resample, "r")
graph_resample = f.read()
f.close()
f = open(path_zen, "r")
graph_zen = f.read()
f.close()
f = open(path_LC, "r")
graph_LC = f.read()
f.close()
f = open(path_ele, "r")
graph_ele = f.read()
f.close()
f = open(path_cut, "r")
graph_cut = f.read()
f.close()
f = open(path_s3_pro, "r")
graph_s3_pro = f.read()
f.close()

# Creatin of script and xml file for S2
file_path_s2 = open(path_file_path_s2, "r")
script_text = ""
date_s2 = ""
for line in file_path_s2:
    s2_image_path = line.strip()
    path = "\\".join(s2_image_path.split("\\")[:-2])
    date = " ".join(s2_image_path.split("\\")[-3:-2])
    date_s2 = date_s2 + date + "\n"
    
    # Mask file
    mask_image = path + "\\S2_" + date + "_mask.dim"
    text_mask = graph_bandmask.replace("!INPUT_Sentinel-2_L2A!", s2_image_path).replace("!OUTPUT_mask!", mask_image)
    path_mask = path_graph + "BandMaths_mask_sentinel_2_pre_processing_"  + date +".xml"
    script_text = script_text + "gpt " + path_mask + "\n"
    f = open(path_mask, "w")
    f.write(text_mask)
    f.close()
    
    # Biophysical
    bio_image = path + "\\S2_" + date + "_biophysical.dim"
    text_bio = graph_bio.replace("!INPUT_Sentinel-2_L2A!", s2_image_path).replace("!OUTPUT_biophysical!", bio_image)
    path_bio = path_graph + "BiophysicalOp_sentinel_2_pre_processing_"  + date +".xml"
    script_text = script_text + "gpt " + path_bio + "\n"
    f = open(path_bio, "w")
    f.write(text_bio)
    f.close()
    
    # Reflectance
    refl_image = path + "\\S2_" + date + "_reflectance.dim"
    text_refl = graph_refl.replace("!INPUT_Sentinel-2_L2A!", s2_image_path).replace("!OUTPUT_reflectance!", refl_image)
    path_refl = path_graph + "reflectance_sentinel_2_pre_processing_"  + date +".xml"
    script_text = script_text + "gpt " + path_refl + "\n"
    f = open(path_refl, "w")
    f.write(text_refl)
    f.close()
    
    # Resample
    resample_image = path + "\\S2_" + date + "_resampled.dim"
    text_resample = graph_resample.replace("!INPUT_Sentinel-2_L2A!", s2_image_path).replace("!OUTPUT_resampled!", resample_image)
    path_resample = path_graph + "resample_sentinel_2_pre_processing_"  + date +".xml"
    script_text = script_text + "gpt " + path_resample + "\n"
    f = open(path_resample, "w")
    f.write(text_resample)
    f.close()
    
    # Sun Zenith
    zen_image = path + "\\S2_" + date + "_sun_zenith_angle.dim"
    text_zen = graph_zen.replace("!INPUT_Sentinel-2_L2A!", s2_image_path).replace("!OUTPUT_sun_zenith_angle!", zen_image)
    path_zen = path_graph + "sun_zenith_sentinel_2_pre_processing_"  + date +".xml"
    script_text = script_text + "gpt " + path_zen + "\n"
    f = open(path_zen, "w")
    f.write(text_zen)
    f.close()
    
    # Landcover
    LC_image = path + "\\S2_" + date + "_landcover.dim"
    text_LC = graph_LC.replace("!INPUT_Sentinel-2_Mask!", mask_image).replace("!OUTPUT_CCI_landcover!", LC_image)
    path_LC = path_graph + "add_landcover_"  + date +".xml"
    script_text = script_text + "gpt " + path_LC + "\n"
    f = open(path_LC, "w")
    f.write(text_LC)
    f.close()

    # Elevation
    ele_image = path + "\\S2_" + date + "_elevation.dim"
    text_ele = graph_ele.replace("!INPUT_Sentinel-2_Mask!", mask_image).replace("!OUTPUT_SRTM_elevation!", ele_image)
    path_ele = path_graph + "add_elevation_"  + date +".xml"
    script_text = script_text + "gpt " + path_ele + "\n" +"\n\n"
    f = open(path_ele, "w")
    f.write(text_ele)
    f.close()
file_path_s2.close()

# Creatin of script and xml file for S3
file_path_s3 = open(path_file_path_s3, "r")
date_s3 = ""
for line in file_path_s3:
    s3_image_path = line.strip()
    path = "\\".join(s3_image_path.split("\\")[:-2])
    date = " ".join(s3_image_path.split("\\")[-3:-2])
    date_s3 = date_s3 + date + "\n"
    
    # Cut
    cut_image = path + "\\S3_" + date + "_cut.dim"
    text_cut = graph_cut.replace("!INPUT_Sentinel-3_LST!", s3_image_path).replace("!INPUT_AOI_WKT!", AOI_WTK).replace("!OUTPUT_Sentinel-3_cut!", cut_image)
    path_cut = path_graph + "sentinel_3_cut_"  + date +".xml"
    script_text = script_text + "gpt " + path_cut + "\n"
    f = open(path_cut, "w")
    f.write(text_cut)
    f.close()
    
    # Processing
    obs_image = path + "\\S3_" + date + "_obs_geometry.dim"
    mask_image = path + "\\S3_" + date + "_mask.dim"
    lst_image = path + "\\S3_" + date + "_lst.dim"
    text_s3_pro = graph_s3_pro.replace("!INPUT_Sentinel-3_LST!", cut_image).replace("!INPUT_AOI_WKT!", AOI_WTK).replace("!OUTPUT_observation_geometry!", obs_image).replace("!OUTPUT_mask!", mask_image).replace("!OUTPUT_LST!", lst_image)
    path_s3_pro = path_graph + "sentinel_3_preprocessing_fix_"  + date +".xml"
    script_text = script_text + "gpt " + path_s3_pro + "\n" + "\n\n"
    f = open(path_s3_pro, "w")
    f.write(text_s3_pro)
    f.close()
file_path_s3.close()

script_text = script_text.replace("\\", "\\\\")

# Save file date and scirpt
f = open(path_date_s2, "w")
f.write(date_s2)
f.close()
f = open(path_date_s3, "w")
f.write(date_s3)
f.close()
f = open(path_script, "w")
f.write(script_text)
f.close()

print("Script created!\n" + path_script)