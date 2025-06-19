
"""
Author: Antoine Duplantie
Date: 2025-04-28
Version: 0.1
Email: aduplantie-grenier@transitionaccelerator.ca

Description:
-------------
This script processes energy modeling output data for the Net-Zero scenario.
It loads the raw CSV, melts the data into a long format, maps technical codes 
(sector, subsector, carrier, technology, province) into human-readable names 
using predefined dictionaries, and exports the cleaned dataset for visualization 
and analysis.

If you have any questions, please contact the author at the email above.
"""

import pandas as pd

excel_files_NZ = "/Users/antoineduplantie-grenier/Desktop/Modeling/VIZ/Output/Net-zero scenario - Master.csv"


df_NZ = pd.read_csv(excel_files_NZ)



subsector_dict_NZ = {
    "Agr": "Agri",
    "Com": "Comm",
    "MfgInd": "Mfg",
    "ExtInd": "Extract",
    "Res": "Resid",
    "PersTrans": "PersTrans",
    "Freight": "Freight"
}

tech_dict = {
    "Am_ice": "Ammonia Internal Combustion Engine",
    "H2_fcev": "Hydrogen Fuel Cell Electric Vehicle",
    "H2_ice": "Hydrogen Internal Combustion Engine",
    "d_ice": "Diesel Internal Combustion Engine",
    "db_ice": "Biodiesel Internal Combustion Engine",
    "dr_ice": "Renewable Diesel Internal Combustion Engine",
    "e_bev": "Battery Electric Vehicle",
    "et_ice": "Ethanol Internal Combustion Engine",
    "j_ice": "Jet Fuel Internal Combustion Engine",
    "jr_ice": "Renewable Jet Fuel Internal Combustion Engine",
    "p_ice": "Propane Internal Combustion Engine",
    "pr_ice": "Renewable Propane Internal Combustion Engine",
    "Am_boil": "Ammonia Boiler",
    "H2_boil": "Hydrogen Boiler",
    "H2_hef": "Hydrogen High-Efficiency Furnace",
    "e_ccashp": "Cold Climate Air Source Heat Pump (Electric)",
    "e_gshp": "Ground Source Heat Pump (Electric)",
    "e_resht": "Residential Electric Space Heating",
    "hfo_boil": "Heavy Fuel Oil Boiler",
    "lfo_boil": "Light Fuel Oil Boiler",
    "ng_mef": "Natural Gas Medium-Efficiency Furnace",
    "ngr_hef": "Renewable Natural Gas High-Efficiency Furnace",
    "pro_mef": "Propane Medium-Efficiency Furnace",
    "st_HtXch": "Steam Heat Exchanger",
    "H2_cook": "Hydrogen Cooking",
    "e_cook": "Electric Cooking",
    "e_othbldg": "Electric Other Building Use",
    "ng_cook": "Natural Gas Cooking",
    "ngr_cook": "Renewable Natural Gas Cooking",
    "pro_cook": "Propane Cooking",
    "e_ashp": "Air Source Heat Pump (Electric)",
    "e_solar": "Solar Thermal Heating (Electric Auxiliary)",
    "ng_boil": "Natural Gas Boiler",
    "ngr_boil": "Renewable Natural Gas Boiler",
    "pro_boil": "Propane Boiler",
    "H2_hwt": "Hydrogen Hot Water Tank",
    "e_hwod": "Electric Hot Water On Demand",
    "e_hwt": "Electric Hot Water Tank",
    "hfo_hwt": "Heavy Fuel Oil Hot Water Tank",
    "lfo_hwt": "Light Fuel Oil Hot Water Tank",
    "ng_hwt": "Natural Gas Hot Water Tank",
    "ngr_hwt": "Renewable Natural Gas Hot Water Tank",
    "pro_hwt": "Propane Hot Water Tank",
    "e_fs": "Electric Facility Support",
    "Am_icemd": "Ammonia Internal Combustion Machine Drive",
    "H2_fcmd": "Hydrogen Fuel Cell Machine Drive",
    "H2_icemd": "Hydrogen Internal Combustion Machine Drive",
    "dr_icemd": "Renewable Diesel Internal Combustion Machine Drive",
    "e_gridmd": "Electric Grid-Powered Machine Drive",
    "ng_icemd": "Natural Gas Internal Combustion Machine Drive",
    "e_op": "Electric Other Processes",
    "Am_ph": "Ammonia Process Heat",
    "H2_ph": "Hydrogen Process Heat",
    "c_ph": "Coal Process Heat",
    "cCS_ph": "Coal with Carbon Capture Process Heat",
    "dr_ph": "Renewable Diesel Process Heat",
    "e_ph": "Electric Process Heat",
    "ng_ph": "Natural Gas Process Heat",
    "ngCS_ph": "Natural Gas with Carbon Capture Process Heat",
    "pl_ph": "Petroleum Liquids Process Heat",
    "st_ph": "Steam Process Heat",
    "w_ph": "Wood Process Heat",
    "d_icemd": "Diesel Internal Combustion Machine Drive",
    "Am_icepg": "Ammonia Internal Combustion Power Generation",
    "H2_fcpg": "Hydrogen Fuel Cell Power Generation",
    "H2_icepg": "Hydrogen Internal Combustion Power Generation",
    "d_icepg": "Diesel Internal Combustion Power Generation",
    "dr_icepg": "Renewable Diesel Internal Combustion Power Generation",
    "e_grid": "Electric Grid Supply",
    "d_ph": "Diesel Process Heat",
    "hfo_ph": "Heavy Fuel Oil Process Heat",
    "ng_icepg": "Natural Gas Internal Combustion Power Generation",
    "hfo_icepg": "Heavy Fuel Oil Internal Combustion Power Generation",
    "w_cook": "Wood Cooking",
    "lfo_mef": "Light Fuel Oil Medium-Efficiency Furnace",
    "lfo_nef": "Light Fuel Oil New-Efficiency Furnace",
    "ng_hef": "Natural Gas High-Efficiency Furnace",
    "ng_nef": "Natural Gas New-Efficiency Furnace",
    "w_stove": "Wood Stove Heating",
    "wp_gasif": "Wood Pellets Gasification",
    "wp_pellet": "Wood Pellet Combustion",
    "e_solarw": "Solar Water Heating (Electric Backup)",
    "w_hwt": "Wood Hot Water Tank",
    "ng_ice": "Natural Gas Internal Combustion Engine",
    "pro_ice": "Propane Internal Combustion Engine",
    "st_HtXch": "Steam Heat Exchanger",
    "H2_FCEV": "Hydrogen Fuel Cell Electric Vehicle",
    "st_htXch" : "Steam Heat Exchanger",
    "-":"-"
}

Province_real_NZ = {
    "AB" : "Alberta",
    "QC" : "Quebec",
    "SK" : "Sasktchewan",
    "ATL" : "Atlantic Provinces",
    "BCT" : "British-Columbia",
    "ON" : "Ontario",
    "MB": "Manitoba",
    "CA":"Canada"    
}

sector_activity_dict_NZ = {
    "Mot": "Motive Power",
    "Nmot": "Non-Motive Power",
    "COth": "Commercial Other",
    "CSH": "Commercial Space Heating",
    "CWH": "Commercial Water Heating",
    
    "Cement_fs": "Cement Facility Support",
    "Cement_md": "Cement Machine Drive",
    "Cement_op": "Cement Other Processes",
    "Cement_ph": "Cement Process Heat",
    "Cement_tr": "Cement Transportation",
    
    "Chem_fs": "Chemicals Facility Support",
    "Chem_md": "Chemicals Machine Drive",
    "Chem_op": "Chemicals Other Processes",
    "Chem_pg": "Chemicals Power Generation",
    "Chem_ph": "Chemicals Process Heat",
    "Chem_tr": "Chemicals Transportation",
    
    "Const_pg": "Construction Power Generation",
    "Const_ph": "Construction Process Heat",
    "Const_tr": "Construction Transportation",
    
    "Cu mine_fs": "Copper Mining Facility Support",
    "Cu mine_md": "Copper Mining Machine Drive",
    "Cu mine_op": "Copper Mining Other Processes",
    "Cu mine_ph": "Copper Mining Process Heat",
    "Cu mine_pg": "Copper Mining Power Generation",
    "Cu mine_tr": "Copper Mining Transportation",
    
    "Forest_pg": "Forestry Power Generation",
    "Forest_tr": "Forestry Transportation",
    "Forest_ph": "Forestry Process Heat",
    
    "I&S_fs": "Iron and Steel Facility Support",
    "I&S_md": "Iron and Steel Machine Drive",
    "I&S_op": "Iron and Steel Other Processes",
    "I&S_pg": "Iron and Steel Power Generation",
    "I&S_ph": "Iron and Steel Process Heat",
    "I&S_tr": "Iron and Steel Transportation",
    
    "Manuf_fs": "Manufacturing Facility Support",
    "Manuf_md": "Manufacturing Machine Drive",
    "Manuf_op": "Manufacturing Other Processes",
    "Manuf_pg": "Manufacturing Power Generation",
    "Manuf_ph": "Manufacturing Process Heat",
    "Manuf_tr": "Manufacturing Transportation",
    
    "O non-met_fs": "Other Non-Metallic Facility Support",
    "O non-met_md": "Other Non-Metallic Machine Drive",
    "O non-met_pg": "Other Non-Metallic Power Generation",
    "O non-met_ph": "Other Non-Metallic Process Heat",
    "O non-met_tr": "Other Non-Metallic Transportation",
    
    "Salt_fs": "Salt Mining Facility Support",
    "Salt_md": "Salt Mining Machine Drive",
    "Salt_ph": "Salt Mining Process Heat",
    "Salt_tr": "Salt Mining Transportation",
    
    "Smelt_fs": "Smelting Facility Support",
    "Smelt_md": "Smelting Machine Drive",
    "Smelt_op": "Smelting Other Processes",
    "Smelt_ph": "Smelting Process Heat",
    "Smelt_tr": "Smelting Transportation",
    
    "p&p_fs": "Pulp and Paper Facility Support",
    "p&p_md": "Pulp and Paper Machine Drive",
    "p&p_op": "Pulp and Paper Other Processes",
    "p&p_pg": "Pulp and Paper Power Generation",
    "p&p_ph": "Pulp and Paper Process Heat",
    "p&p_tr": "Pulp and Paper Transportation",
    
    "ROth": "Residential Other",
    "RSH": "Residential Space Heating",
    "RWH": "Residential Water Heating",
    
    "Air": "Aviation",
    "HDV": "Heavy Duty Vehicles",
    "ICB": "Intercity Buses",
    "LDV": "Light Duty Vehicles",
    "MDV": "Medium Duty Vehicles",
    "Off-Road": "Off-Road Vehicles and Equipment",
    "Rail": "Rail Transportation",
    "SB": "School Buses",
    "UB": "Urban Buses",
    
    "G&S mine_fs": "Gold and Silver Mining Facility Support",
    "G&S mine_md": "Gold and Silver Mining Machine Drive",
    "G&S mine_op": "Gold and Silver Mining Other Processes",
    "G&S mine_pg": "Gold and Silver Mining Power Generation",
    "G&S mine_ph": "Gold and Silver Mining Process Heat",
    "G&S mine_tr": "Gold and Silver Mining Transportation",
    
    "I mine_fs": "Iron Mining Facility Support",
    "I mine_md": "Iron Mining Machine Drive",
    "I mine_op": "Iron Mining Other Processes",
    "I mine_pg": "Iron Mining Power Generation",
    "I mine_ph": "Iron Mining Process Heat",
    "I mine_tr": "Iron Mining Transportation",
    
    "O metal_fs": "Other Metals Facility Support",
    "O metal_md": "Other Metals Machine Drive",
    "O metal_op": "Other Metals Other Processes",
    "O metal_pg": "Other Metals Power Generation",
    "O metal_ph": "Other Metals Process Heat",
    "O metal_tr": "Other Metals Transportation",
    
    "Alum_fs": "Aluminum Facility Support",
    "Alum_md": "Aluminum Machine Drive",
    "Alum_op": "Aluminum Other Processes",
    "Alum_ph": "Aluminum Process Heat",
    "Alum_tr": "Aluminum Transportation",
    
    "K mine_fs": "Potash Mining Facility Support",
    "K mine_md": "Potash Mining Machine Drive",
    "K mine_ph": "Potash Mining Process Heat",
    "K mine_tr": "Potash Mining Transportation",
    
    "All": "All Sectors"
}



# Map fuel carrier codes to readable names (example: 'd' -> 'Diesel')
df_NZ["Province"] = df_NZ["Region"].map(Province_real_NZ)

df_NZ["Tech_subsector"] = df_NZ["Subsector"].map(sector_activity_dict_NZ)

df_NZ[" Tech_name"] = df_NZ["tech"].map(tech_dict)


# Define output path for the melted and processed Status-Quo dataset
output_path = "/Users/antoineduplantie-grenier/Desktop/Modeling/VIZ/NZ_Post_Process.csv"
# Export the final DataFrame to CSV, without including the index
df_NZ.to_csv(output_path, index=False)

