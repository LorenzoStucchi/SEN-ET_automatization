from datetime import datetime
import json
from shapely.geometry import Polygon

def extract_s3_bbox(coord_list):
    x = []
    y = []
    for i in range(0,len(coord_list),2):
        x.append(float(coord_list[i+1]))
        y.append(float(coord_list[i]))
    x1 = []
    x2 = []
    k1 = 0
    k2 = -360
    zip_object = zip(x[:-1], x[1:])
    for list1_i, list2_i in zip_object:
        l_diff = list1_i-list2_i
        if l_diff < -180:
            k1 = 0
            k2 = -360
        elif l_diff > 180:
            k1 = 360
            k2 = 0
        x1.append(list2_i + k1)
        x2.append(list2_i + k2)
    x1.append(x1[0])
    x2.append(x2[0])
    return Polygon([[x1[i], y[i]] for i in range(0,len(x1),2)]), Polygon([[x2[i], y[i]] for i in range(0,len(x2),2)])

path_param = "input/parameters.json"
file_path = "output/path_hour.json"
path_output_s2 = "output/3_script_S2.sh"
path_output_s3 = "output/4_script_S3.sh"
path_graph_et = "graph/et_tiff_saving.xml"

# Open graph for save ET as tiff
f = open(path_graph_et, "r")
graph_et = f.read()
f.close()

with open(path_param, "r") as f:
    p = json.load(f)
with open(file_path, "r") as f:
    images = json.load(f)["data"]

# Parameters
intermediate_path = p["temp_files"]
et_path = p["output_files"]
python_path = p["senet_folder"]
min_frac_green = str(p["comp_parameters"]["frac_green"]["min_frac_green"])
soil_roughness_ae = str(p["comp_parameters"]["aerodynamic_roughness"]["soil_roughness"])
algorithm = str(p["comp_parameters"]["warp"]["algorithm"])
cv_homogeneity_threshold = str(p["comp_parameters"]["data_mining"]["cv_homogeneity_threshold"])
moving_window_size = str(p["comp_parameters"]["data_mining"]["moving_window_size"])
parallel_jobs = str(p["comp_parameters"]["data_mining"]["parallel_jobs"])
time_zone = str(p["comp_parameters"]["ecwf_data"]["time_zone"])
soil_ref_vis = str(p["comp_parameters"]["shortwave_radiation"]["soil_ref_vis"])
soil_ref_nir = str(p["comp_parameters"]["shortwave_radiation"]["soil_ref_nir"])
soil_roughness_en = str(p["comp_parameters"]["energy_fluxes"]["soil_roughness"])
alpha_pt = str(p["comp_parameters"]["energy_fluxes"]["alpha_pt"])
green_vegetation_emissivity = str(p["comp_parameters"]["energy_fluxes"]["green_vegetation_emissivity"])
soil_emissivity = str(p["comp_parameters"]["energy_fluxes"]["soil_emissivity"])
lookup_table = python_path + "/sen-et-snap-scripts/auxdata/LUT/ESA_CCI_LUT.csv"

general_path_era_meteo = "input/era/era5.nc"
general_path_era = intermediate_path + "/era/TILE/YYYY/MM/DD/"
text = ""
s2_list = []
s3_list = []
combs = []

# Command list
cmd_leaf = "time " + python_path + "/bin/python " + python_path + "/sen-et-snap-scripts/leaf_spectra.py --biophysical_file PATHS2/biophysical.dim --output_file PATHS2/leaf_spectra.dim"
cmd_fracgreen = "time " + python_path + "/bin/python " + python_path + "/sen-et-snap-scripts/frac_green.py --sza_file PATHS2/sun_zenith_angle.dim --biophysical_file PATHS2/biophysical.dim --min_frac_green " + min_frac_green + " --output_file PATHS2/frac_green.dim"
cmd_strpar = "time " + python_path + "/bin/python " + python_path + "/sen-et-snap-scripts/structural_params.py --landcover_map PATHS2/landcover.dim --lai_map PATHS2/biophysical.dim --fgv_map PATHS2/frac_green.dim --landcover_band land_cover_CCILandCover-2015 --lookup_table " + lookup_table + " --produce_vh 1 --produce_fc 1 --produce_chwr 1 --produce_lw 1 --produce_lid 1 --produce_igbp 1 --output_file PATHS2/structural_parameters.dim"
cmd_aero = "time " + python_path + "/bin/python " + python_path + "/sen-et-snap-scripts/aerodynamic_roughness.py --lai_map PATHS2/biophysical.dim --landcover_params_map PATHS2/structural_parameters.dim --soil_roughness " + soil_roughness_ae + " --output_file PATHS2/aerodynamic_parameters.dim"
cmd_warp = "time " + python_path + "/bin/python " + python_path + "/sen-et-snap-scripts/warp_to_template.py --source PATHS3/obs_geometry.dim --template PATHS2/mask.dim --resample_algorithm " + algorithm + " --output PATHS3/hr_vza.dim"
cmd_sharp = "time " + python_path + "/bin/python " + python_path + "/sen-et-snap-scripts/data_mining_sharpener.py --sentinel_2_reflectance PATHS2/reflectance.dim --sentinel_3_lst PATHS3/lst.dim --high_res_dem PATHS2/elevation.dim --high_res_geom PATHS3/hr_vza.dim --lst_quality_mask PATHS3/mask.dim --date_time_utc \"DATA\" --elevation_band elevation --lst_good_quality_flags 1 --cv_homogeneity_threshold " + cv_homogeneity_threshold + " --moving_window_size " + moving_window_size + " --parallel_jobs " + parallel_jobs + " --output PATHS3/lst_sharpened.dim"
cmd_ecmwf = "time " + python_path + "/bin/python " + python_path + "/sen-et-snap-scripts/ecmwf_data_preparation.py --elevation_map PATHS2/elevation.dim --elevation_band elevation --ecmwf_data_file " + general_path_era_meteo + " --date_time_utc \"DATA\" --time_zone " + time_zone + " --prepare_temperature 1 --prepare_vapour_pressure 1 --prepare_air_pressure 1 --prepare_wind_speed 1 --prepare_clear_sky_solar_radiation 1 --prepare_daily_solar_irradiance 1 --output_file PATHERAmeteo.dim"
cmd_long = "time " + python_path + "/bin/python " + python_path + "/sen-et-snap-scripts/longwave_irradiance.py --meteo_product PATHERAmeteo.dim --at_band air_temperature --vp_band vapour_pressure --ap_band air_pressure --at_height 100 --output_file PATHOUT_longwave_ir.dim"
cmd_short = "time " + python_path + "/bin/python " + python_path + "/sen-et-snap-scripts/net_shortwave_radiation.py --lsp_product PATHS2/leaf_spectra.dim --lai_product PATHS2/biophysical.dim --csp_product PATHS2/structural_parameters.dim --mi_product PATHERAmeteo.dim --sza_product PATHS3/hr_vza.dim --soil_ref_vis " + soil_ref_vis + " --soil_ref_nir " + soil_ref_nir + " --output_file PATHOUT_shortwave_ra.dim"
cmd_fluxes = "time " + python_path + "/bin/python " + python_path + "/sen-et-snap-scripts/energy_fluxes.py --lst PATHS3/lst_sharpened.dim --lst_vza PATHS3/hr_vza.dim --lai PATHS2/biophysical.dim --csp PATHS2/structural_parameters.dim --fgv PATHS2/frac_green.dim --ar PATHS2/aerodynamic_parameters.dim --mi PATHERAmeteo.dim --nsr PATHOUT_shortwave_ra.dim --li PATHOUT_longwave_ir.dim --mask PATHS2/mask.dim --soil_roughness " + soil_roughness_en + " --alpha_pt " + alpha_pt + " --atmospheric_measurement_height 100 --green_vegetation_emissivity " + green_vegetation_emissivity + " --soil_emissivity " + soil_emissivity + " --save_component_fluxes 1 --save_component_temperature 1 --save_aerodynamic_parameters 1 --output_file PATHOUT_instantaneous_fluxes.dim"
cmd_et = "time " + python_path + "/bin/python " + python_path + "/sen-et-snap-scripts/daily_evapotranspiration.py --ief_file PATHOUT_instantaneous_fluxes.dim --mi_file PATHERAmeteo.dim --output_file PATHET_daily_evapotranspiration.dim"

for image in images:
    if image["platform"] == "S2":
        date = image["day"]
        tile = image["tile"]
        t_general_path_s2 = image["derived_product_path"]
        text = text + "echo \"\t Computing the leaf parameters for the image S2 " + date + "_" + tile + "\"\n"
        text = text + cmd_leaf.replace("PATHS2", t_general_path_s2) + "\n"
        text = text + "echo \"Computed the leaf parameters for the image S2 " + date + "_" + tile + "\"\n"
        text = text + "echo \"\t Computing the fraction of green for the image S2 " + date + "_" + tile + "\"\n"
        text = text + cmd_fracgreen.replace("PATHS2", t_general_path_s2) + "\n"
        text = text + "echo \"Computed the fraction of green for the image S2 " + date + "_" + tile + "\"\n"
        text = text + "echo \"\t Computing the structural parameters for the image S2 " + date + "_" + tile + "\"\n"
        text = text + cmd_strpar.replace("PATHS2", t_general_path_s2) + "\n"
        text = text + "echo \"Computed the structural parameters for the image S2 " + date + "_" + tile + "\"\n"
        text = text + "echo \"\t Computing the aerodynamic parameters for the image S2 " + date + "_" + tile + "\"\n"
        text = text + cmd_aero.replace("PATHS2", t_general_path_s2) + "\n"
        text = text + "echo \"Computed the aerodynamic parameters for the image S2 " + date + "_" + tile + "\"\n\n"  

f = open(path_output_s2, "w")
f.write(text)
f.close()

text = ""

# Check combination s2 and s3 based on time and bbox
for image in images:
    if image["platform"] == "S2":
        for line in open(image["path"], 'r').readlines():
            if "<EXT_POS_LIST>" in line:
                b_s2 = line.strip()[14:][:-15].strip().split(" ")
                break
        s2_bbox = Polygon([[float(b_s2[i+1]), float(b_s2[i])] for i in range(0,len(b_s2),2)])
        s2_list.append([int(image["uid"]), s2_bbox])
    elif image["platform"] == "S3":
        for line in open(image["path"], 'r').readlines():
            if "gml:posList" in line:
                b_s3 = line.strip()[13:][:-14].strip().split(" ")
                break
        s3_bbox, s3_bbox_alt = extract_s3_bbox(b_s3)
        s3_list.append([int(image["uid"]), s3_bbox, s3_bbox_alt])

# Spatial control of the couples
for s2 in s2_list:
    data_s2 = images[s2[0]]["day"]
    for s3 in s3_list:
        data_s3 = images[s3[0]]["day"]
        delta = datetime.strptime(data_s3, "%Y_%m_%d") - datetime.strptime(data_s2, "%Y_%m_%d")
        if ( s3[1].contains(s2[1]) or s3[2].contains(s2[1]) ) and delta.days <= 10:
            combs.append([s2[0], s3[0]])

# for each combination create che corrispoding S3 operation
for comb in combs:
    s2 = images[comb[0]]
    s3 = images[comb[1]]

    year = s3["day"][:4]
    mon = s3["day"][5:7]
    day = s3["day"][8:10]
    date = s3["day"].replace("_","-") + " " + s3["hour"]

    t_general_path_s2 = s2["derived_product_path"]
    t_general_path_s3 = s3["derived_product_path"]
    t_general_path_era = general_path_era.replace("YYYY", year).replace("MM", mon).replace("DD", day).replace("TILE", s2["tile"])
    t_general_path_out = s3["derived_product_path"]
    t_general_path_et = s3["derived_product_path"]
    t_general_path_et_tiff = et_path + "/" + s3["day"] + "_" + s2["tile"] + "_" + s3["tile"]

    text = text + "echo \"\t Warp the image S3 " + date + "\"\n"
    text = text + cmd_warp.replace("PATHS3", t_general_path_s3).replace("PATHS2", t_general_path_s2) + "\n"
    
    text = text + "echo \"\t Sharpening the image S3 " + date + "\"\n"
    text = text + cmd_sharp.replace("PATHS3", t_general_path_s3).replace("PATHS2", t_general_path_s2).replace("DATA", date) + "\n"
    text = text + "echo \"Sharpened the image S3 " + date + "\"\n"
    
    text = text + "echo \"\t Computing the meteo data for the day " + date + "\"\n"
    text = text + cmd_ecmwf.replace("PATHS2", t_general_path_s2).replace("DATA", date.replace("_","-")).replace("PATHERA", t_general_path_era) + "\n"
    text = text + "echo \"Computed the meteo data for the day " + date + "\"\n"
    
    text = text + "echo \"\t Computing the longwave radiation for the image S3 " + date + "\"\n"
    text = text + cmd_long.replace("PATHERA", t_general_path_era).replace("PATHOUT", t_general_path_out) + "\n"
    text = text + "echo \"Computed the longwave radiation for the image S3 " + date + "\"\n"
    
    text = text + "echo \"\t Computing the shortwave radiation for the image S3 " + date + "\"\n"
    text = text + cmd_short.replace("PATHS3", t_general_path_s3).replace("PATHS2", t_general_path_s2).replace("PATHERA", t_general_path_era).replace("PATHOUT", t_general_path_out) + "\n"
    text = text + "echo \"Computed the shortwave radiation for the image S3 " + date + "\"\n"
    
    text = text + "echo \"\t Computing the energy fluxes for the image S3 " + date + "\"\n"
    text = text + cmd_fluxes.replace("PATHS3", t_general_path_s3).replace("PATHS2", t_general_path_s2).replace("PATHERA", t_general_path_era).replace("PATHOUT", t_general_path_out) + "\n"
    text = text + "echo \"Computed the energy fluxes for the image S3 " + date + "\"\n"
    
    text = text + "echo \"\t Computing the evapotranspiration for the image S3 " + date + "\"\n"
    text = text + cmd_et.replace("PATHERA", t_general_path_era).replace("PATHOUT", t_general_path_out).replace("PATHET", t_general_path_et) + "\n"
    text = text + "echo \"Computed the evapotranspiration for the image S3 " + date + "\"\n"
    
    # Write ET as geotiff
    text = text + "echo \"\t Saving the evapotranspiration maps into TIFF for the image S3 " + date + "\"\n"
    text_grapht_et = graph_et.replace("!INPUT_et_DIM!", t_general_path_et + "_daily_evapotranspiration.dim").replace("!OUTPUT_et_GEOTIFF!", t_general_path_et_tiff + "_daily_evapotranspiration.tif")
    path_grapht_et = s2["derived_product_path"] + "/graph/et_tiff_saving_" + s3["day"] + "_" + s3["tile"] + "_" + s2["tile"] + ".xml"
    text = text + "time -v gpt " + path_grapht_et + "\n"
    text = text + "echo \"Saved the evapotranspiration maps into TIFF for the image S3 " + date + "\"\n"
    f = open(path_grapht_et, "w")
    f.write(text_grapht_et)
    f.close()

    text = text + "echo \"\t Finish the computation of the evapotranspiration for the image S3 " + date + "\"\n\n"

text = text.replace("\\", "\\\\")
f = open(path_output_s3, "w")
f.write(text)
f.close()
    
# Show results
print("\tScripts created!\n\t" + path_output_s2 + "\n\t" + path_output_s3)