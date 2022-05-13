import os
import json
path_param = "input/parameters.json"
path_file_path_s2 = "input/s2_paths.txt"
path_file_path_s3 = "input/s3_paths.txt"
path_bandmask = "graph/BandMaths_mask_sentinel_2_pre_processing.xml"
path_bio = "graph/BiophysicalOp_sentinel_2_pre_processing.xml"
path_refl = "graph/reflectance_sentinel_2_pre_processing.xml"
path_resample = "graph/resample_sentinel_2_pre_processing.xml"
path_zen = "graph/sun_zenith_sentinel_2_pre_processing.xml"
path_LC = "graph/add_landcover.xml"
path_ele = "graph/add_elevation.xml"
path_cut = "graph/sentinel_3_cut.xml"
path_s3_pro = "graph/sentinel_3_pre_processing_fix.xml"
path_graph = "output/graph/"
path_date_s2 = "output/days_s2.txt"
path_date_s3 = "output/days_s3.txt"
path_script_s3 = "output/1_script_gpt_s3.sh"
path_script_s2 = "output/2_script_gpt_s2.sh"

# Create directory
if os.path.isdir("output") == False:
    os.mkdir("output")
    os.mkdir("output/graph")
else:
    if os.path.isdir("output/graph") == False:
        os.mkdir("output/graph")

# Definition of general varibles
with open(path_param, "r") as f:
    param = json.load(f)
AOI_WTK = "POLYGON ((" + str(param["AOI"]["west"]) + " " + str(param["AOI"]["north"]) + ", " + str(param["AOI"]["est"]) + " " + str(param["AOI"]["north"]) + ", " + str(param["AOI"]["est"]) + " " + str(param["AOI"]["south"]) + ", " + str(param["AOI"]["west"]) + " " + str(param["AOI"]["south"]) + ", " + str(param["AOI"]["west"]) + " " + str(param["AOI"]["north"]) + ", " + str(param["AOI"]["west"]) + " " + str(param["AOI"]["north"]) + "))"
general_path = param["general_path"]
intermediate_output_path = param["temp_files"]

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

# Creatin of script and xml file for S3
file_path_s3 = open(path_file_path_s3, "r")
script_text = ""
date_s3 = ""
for line in file_path_s3:
    s3_image_path = line.strip()
    path = intermediate_output_path + "/" + "/".join(s3_image_path.split("/")[-7:-1])
    date = "_".join(s3_image_path.split("/")[-4:-1])
    date_s3 = date_s3 + date + "\n"
    s3_image_path = s3_image_path + "/xfdumanifest.xml"

    # Cut
    script_text = script_text + "echo \"\t Cut the image S3 " + date + "\"\n"
    cut_image = path + "/S3_" + date + "_cut.dim"
    text_cut = graph_cut.replace("!INPUT_Sentinel-3_LST!", s3_image_path).replace("!INPUT_AOI_WKT!", AOI_WTK).replace("!OUTPUT_Sentinel-3_cut!", cut_image)
    path_cut = path_graph + "sentinel_3_cut_"  + date +".xml"
    script_text = script_text + "time gpt " + path_cut + "\n"
    script_text = script_text + "echo \"Cut the image S3 " + date + "\"\n"
    f = open(path_cut, "w")
    f.write(text_cut)
    f.close()

    # Processing
    script_text = script_text + "echo \"\t Processing the image S3 " + date + "\"\n"
    obs_image = path + "/S3_" + date + "_obs_geometry.dim"
    mask_image = path + "/S3_" + date + "_mask.dim"
    lst_image = path + "/S3_" + date + "_lst.dim"
    text_s3_pro = graph_s3_pro.replace("!INPUT_Sentinel-3_LST!", cut_image).replace("!INPUT_AOI_WKT!", AOI_WTK).replace("!OUTPUT_observation_geometry!", obs_image).replace("!OUTPUT_mask!", mask_image).replace("!OUTPUT_LST!", lst_image)
    path_s3_pro = path_graph + "sentinel_3_preprocessing_fix_"  + date +".xml"
    script_text = script_text + "time gpt " + path_s3_pro + "\n" 
    script_text = script_text + "echo \"Processed the image S3 " + date + "\"\n" + "\n\n"
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
    tile = s2_image_path.split("/")[-1].split("_")[-2]
    path = intermediate_output_path + "/" + "/".join(s2_image_path.split("/")[-7:-1]) + "/" + tile 
    date = "_".join(s2_image_path.split("/")[-4:-1])
    date_s2 = date_s2 + date + "\n"

    sensor_s2 = " ".join(s2_image_path.split("/")[-1:])[:3]
    s2_image_path = s2_image_path + "/MTD_MSIL2A.xml"
    
    # Mask file
    script_text = script_text + "echo \"\t Computing the mask for the image S2 " + date + "\"\n"
    mask_image = path + "/S2_" + date + "_mask.dim"
    text_mask = graph_bandmask.replace("!INPUT_Sentinel-2_L2A!", s2_image_path).replace("!OUTPUT_mask!", mask_image)
    path_mask = path_graph + "BandMaths_mask_sentinel_2_pre_processing_"  + date +".xml"
    script_text = script_text + "time gpt " + path_mask + "\n"
    script_text = script_text + "echo \"Computed the mask for the image S2 " + date + "\"\n"
    f = open(path_mask, "w")
    f.write(text_mask)
    f.close()
    
    # Biophysical
    script_text = script_text + "echo \"\t Computing the biophysical parameters for the image S2 " + date + "\"\n"
    bio_image = path + "/S2_" + date + "_biophysical.dim"
    text_bio = graph_bio.replace("!INPUT_Sentinel-2_L2A!", s2_image_path).replace("!OUTPUT_biophysical!", bio_image).replace("!INPUT_Sentinel-2_Sensor!", sensor_s2)
    path_bio = path_graph + "BiophysicalOp_sentinel_2_pre_processing_"  + date +".xml"
    script_text = script_text + "time gpt " + path_bio + "\n"
    script_text = script_text + "echo \"Computing the biophysical parameters for the image S2 " + date + "\"\n"
    f = open(path_bio, "w")
    f.write(text_bio)
    f.close()
    
    # Reflectance
    script_text = script_text + "echo \"\t Computing the reflectance for the image S2 " + date + "\"\n"
    refl_image = path + "/S2_" + date + "_reflectance.dim"
    text_refl = graph_refl.replace("!INPUT_Sentinel-2_L2A!", s2_image_path).replace("!OUTPUT_reflectance!", refl_image)
    path_refl = path_graph + "reflectance_sentinel_2_pre_processing_"  + date +".xml"
    script_text = script_text + "time gpt " + path_refl + "\n"
    script_text = script_text + "echo \"Computed the reflectance for the image S2 " + date + "\"\n"
    f = open(path_refl, "w")
    f.write(text_refl)
    f.close()
    
    # Resample
    script_text = script_text + "echo \"\t Resampling the image S2 " + date + "\"\n"
    resample_image = path + "/S2_" + date + "_resampled.dim"
    text_resample = graph_resample.replace("!INPUT_Sentinel-2_L2A!", s2_image_path).replace("!OUTPUT_resampled!", resample_image)
    path_resample = path_graph + "resample_sentinel_2_pre_processing_"  + date +".xml"
    script_text = script_text + "time gpt " + path_resample + "\n"
    script_text = script_text + "echo \"Resampled the image S2 " + date + "\"\n"
    f = open(path_resample, "w")
    f.write(text_resample)
    f.close()
    
    # Sun Zenith
    script_text = script_text + "echo \"\t Computing the sun zenith angular map for the image S2 " + date + "\"\n"
    zen_image = path + "/S2_" + date + "_sun_zenith_angle.dim"
    text_zen = graph_zen.replace("!INPUT_Sentinel-2_L2A!", s2_image_path).replace("!OUTPUT_sun_zenith_angle!", zen_image)
    path_zen = path_graph + "sun_zenith_sentinel_2_pre_processing_"  + date +".xml"
    script_text = script_text + "time gpt " + path_zen + "\n"
    script_text = script_text + "echo \"Computed the sun zenith angular map for the image S2 " + date + "\"\n"
    f = open(path_zen, "w")
    f.write(text_zen)
    f.close()
    
    # Landcover
    script_text = script_text + "echo \"\t Computing the landcover for the image S2 " + date + "\"\n"
    LC_image = path + "/S2_" + date + "_landcover.dim"
    text_LC = graph_LC.replace("!INPUT_Sentinel-2_Mask!", mask_image).replace("!OUTPUT_CCI_landcover!", LC_image)
    path_LC = path_graph + "add_landcover_"  + date +".xml"
    script_text = script_text + "time gpt " + path_LC + "\n"
    script_text = script_text + "echo \"Computed the landcover for the image S2 " + date + "\"\n"
    f = open(path_LC, "w")
    f.write(text_LC)
    f.close()

    # Elevation
    script_text = script_text + "echo \"\t Computing the elevation for the image S2 " + date + "\"\n"
    ele_image = path + "/S2_" + date + "_elevation.dim"
    text_ele = graph_ele.replace("!INPUT_Sentinel-2_Mask!", mask_image).replace("!OUTPUT_SRTM_elevation!", ele_image)
    path_ele = path_graph + "add_elevation_"  + date +".xml"
    script_text = script_text + "time gpt " + path_ele + "\n" 
    script_text = script_text + "echo \"Computed the elevation for the image S2 " + date + "\"\n" + "\n\n"
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