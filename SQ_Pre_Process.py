"""
Author: Antoine Duplantie
Date: 2025-04-28
Version: 0.1
Email: aduplantie-grenier@transitionaccelerator.ca

Description:
-------------
This script processes energy modeling output data for the Status-Quo scenario.
It loads the raw CSV, melts the data into a long format, maps technical codes 
(sector, subsector, carrier, technology, province) into human-readable names 
using predefined dictionaries, and exports the cleaned dataset for visualization 
and analysis.

If you have any questions, please contact the author at the email above.
"""


# Import required library
import pandas as pd


MAX_LABEL_LEN = 20


# === Define mapping dictionaries for translation of codes into descriptive names ===


sector_activity_dict = {
    "Mot": "Mot",
    "Nmot": "Nmot",
    "COth": "COth",
    "CSH": "CSH",
    "CWH": "CWH",
    "Cement_fs": "Cement_fs",
    "Cement_md": "Cement_md",
    "Cement_op": "Cement_op",
    "Cement_ph": "Cement_ph",
    "Cement_tr": "Cement_tr",
    "Chem_fs": "Chem_fs",
    "Chem_md": "Chem_md",
    "Chem_op": "Chem_op",
    "Chem_pg": "Chem_pg",
    "Chem_ph": "Chem_ph",
    "Chem_tr": "Chem_tr",
    "Const_pg": "Const_pg",
    "Const_ph": "Const_ph",
    "Const_tr": "Const_tr",
    "Cu mine_fs": "Cu mine_fs",
    "Cu mine_md": "Cu mine_md",
    "Cu mine_op": "Cu mine_op",
    "Cu mine_ph": "Cu mine_ph",
    "Cu mine_pg": "Cu mine_pg",
    "Cu mine_tr": "Cu mine_tr",
    "Forest_pg": "Forest_pg",
    "Forest_ph": "Forest_ph",
    "Forest_tr": "Forest_tr",
    "I&S_fs": "I&S_fs",
    "I&S_md": "I&S_md",
    "I&S_op": "I&S_op",
    "I&S_pg": "I&S_pg",
    "I&S_ph": "I&S_ph",
    "I&S_tr": "I&S_tr",
    "Manuf_fs": "Manuf_fs",
    "Manuf_md": "Manuf_md",
    "Manuf_op": "Manuf_op",
    "Manuf_pg": "Manuf_pg",
    "Manuf_ph": "Manuf_ph",
    "Manuf_tr": "Manuf_tr",
    "O non-met_fs": "O non-met_fs",
    "O non-met_md": "O non-met_md",
    "O non-met_pg": "O non-met_pg",
    "O non-met_ph": "O non-met_ph",
    "O non-met_tr": "O non-met_tr",
    "Salt_fs": "Salt_fs",
    "Salt_md": "Salt_md",
    "Salt_ph": "Salt_ph",
    "Salt_tr": "Salt_tr",
    "Smelt_fs": "Smelt_fs",
    "Smelt_md": "Smelt_md",
    "Smelt_op": "Smelt_op",
    "Smelt_ph": "Smelt_ph",
    "Smelt_tr": "Smelt_tr",
    "p&p_fs": "p&p_fs",
    "p&p_md": "p&p_md",
    "p&p_op": "p&p_op",
    "p&p_pg": "p&p_pg",
    "p&p_ph": "p&p_ph",
    "p&p_tr": "p&p_tr",
    "ROth": "ROth",
    "RSH": "RSH",
    "RWH": "RWH",
    "Air": "Air",
    "HDV": "HDV",
    "ICB": "ICB",
    "LDV": "LDV",
    "MDV": "MDV",
    "Off-Road": "Off-Road",
    "Rail": "Rail",
    "SB": "SB",
    "UB": "UB",
    "G&S mine_fs": "G&S mine_fs",
    "G&S mine_md": "G&S mine_md",
    "G&S mine_op": "G&S mine_op",
    "G&S mine_pg": "G&S mine_pg",
    "G&S mine_ph": "G&S mine_ph",
    "G&S mine_tr": "G&S mine_tr",
    "I mine_fs": "I mine_fs",
    "I mine_md": "I mine_md",
    "I mine_op": "I mine_op",
    "I mine_pg": "I mine_pg",
    "I mine_ph": "I mine_ph",
    "I mine_tr": "I mine_tr",
    "O metal_fs": "O metal_fs",
    "O metal_md": "O metal_md",
    "O metal_op": "O metal_op",
    "O metal_pg": "O metal_pg",
    "O metal_ph": "O metal_ph",
    "O metal_tr": "O metal_tr",
    "Marine": "Marine",
    "Alum_fs": "Alum_fs",
    "Alum_md": "Alum_md",
    "Alum_op": "Alum_op",
    "Alum_ph": "Alum_ph",
    "Alum_tr": "Alum_tr",
    "K mine_fs": "K mine_fs",
    "K mine_md": "K mine_md",
    "K mine_ph": "K mine_ph",
    "K mine_tr": "K mine_tr"
}

carrier_tech_dict = {
    "d_ice":    "Diesel ICE",
    "db_ice":   "Biodiesel ICE",
    "dr_ice":   "Renewable Diesel ICE",
    "et_ice":   "Ethanol ICE",
    "j_ice":    "Jet ICE",
    "p_ice":    "Gasoline ICE",
    "e_resht":  "Electric Resistive Heat",
    "hfo_boil": "HFO Boiler",
    "lfo_boil": "LFO Boiler",
    "ng_mef":   "NG Mech. Furnace",
    "pro_mef":  "Prop Mech. Furnace",
    "st_HtXch": "Steam Exchanger",
    "e_othbldg":"Elec. Other Bldg.",
    "hfo_othbldg":"HFO Other Bldg.",
    "lfo_othbldg":"LFO Other Bldg.",
    "ng_cook":  "NG Cooking",
    "pro_cook": "Prop Cooking",
    "st_othbldg":"Steam Other Bldg.",
    "ng_boil":  "NG Boiler",
    "pro_boil": "Prop Boiler",
    "e_hwt":    "Elec. Hot Water",
    "hfo_hwt":  "HFO Hot Water",
    "lfo_hwt":  "LFO Hot Water",
    "ng_hwt":   "NG Hot Water",
    "pro_hwt":  "Prop Hot Water",
    "st_hwt":   "Steam Hot Water",
    "e_fs":     "Elec. Facility Support",
    "e_gridmd": "Elec. Grid Drive",
    "ng_icemd": "NG Engine Drive",
    "e_op":     "Elec. Other Processes",
    "c_ph":     "Coal Proc. Heat",
    "e_ph":     "Elec. Proc. Heat",
    "ng_ph":    "NG Proc. Heat",
    "pl_ph":    "Plastics Proc. Heat",
    "st_ph":    "Steam Proc. Heat",
    "d_icemd":  "Diesel Engine Drive",
    "d_icepg":  "Diesel Power Gen",
    "d_ph":     "Diesel Proc. Heat",
    "hfo_ph":   "HFO Proc. Heat",
    "ng_icepg": "NG Power Gen",
    "hfo_icepg":"HFO Power Gen",
    "w_ph":     "Wood Proc. Heat",
    "e_bev":    "Battery EV",
    "lfo_cook": "LFO Cooking",
    "w_cook":   "Wood Cooking",
    "e_ashp":   "Air-Source HP",
    "lfo_hef":  "LFO HE Furnace",
    "lfo_mef":  "LFO Mech. Furnace",
    "lfo_nef":  "LFO Non-Eff. Furnace",
    "ng_hef":   "NG HE Furnace",
    "ng_nef":   "NG Non-Eff. Furnace",
    "w_stove":  "Wood Stove",
    "w_hwt":    "Wood Hot Water",
    "ng_ice":   "NG ICE",
    "pro_ice":  "Prop ICE",
    "hfo_ice":  "HFO ICE",
    "st_htXch": "Steam Heat Exch."
}


abbreviation_dict = {
    "Ag": "Agriculture",
    "Air": "Airplane",
    "Am": "Ammonia",
    "AOSTRA": "Alberta Oil Sand Technology and Research Authority",
    "APEC": "Asia Pacific Energy Research Centre",
    "ATR": "Autothermal Reforming",
    "BECCS": "Bioenergy Carbon Capture and Storage",
    "BEV": "Battery Electric Vehicle",
    "BF": "Biofuel",
    "boil": "boiler",
    "CAPEX": "Capital Expenditure",
    "c": "Coal",
    "cCS": "Coal With Carbon Capture and Storage",
    "CAPP": "Canadian Association of Petroleum Producers",
    "ccashp": "Cold Climate Air Source Heat Pump",
    "CCS": "Carbon and Capture Storage",
    "CER": "Canada Energy Regulator",
    "CH4": "Methane",
    "Chem.": "Chemical Industry",
    "CIE": "Careers in Energy",
    "CO2": "Carbon Dioxide",
    "Com.": "Commercial",
    "COP": "Coefficient of Performance",
    "COth": "Commercial Other Application",
    "CSH": "Commercial Space Heating",
    "CWH": "Commercial Water Heating",
    "d": "Diesel",
    "db": "Biodiesel",
    "dr": "Renewable Diesel",
    "e": "Elec",
    "et": "Ethanol",
    "e_grid": "Electrical Grid",
    "e_gridmd": "Machine Drive Powered by the Electrical Grid",
    "e_op": "Other Processes Powered by Elec",
    "EU": "European Union",
    "Ext. Ind": "Extractive Industries",
    "FCEV": "Fuel Cell Electric Vehicle",
    "fcmd": "Machine Drive Powered by Fuel Cell",
    "fcpg": "Power Generation via Fuel Cell",
    "fs": "Facility Support",
    "gasif": "Gasification",
    "GDP": "Gross Domestic Product",
    "GHG": "Greenhouse Gas",
    "GJ": "Gigajoule",
    "gshp": "Ground Source Heat Pump",
    "GWP": "Global Warming Potential",
    "H2": "Hydrogen",
    "HB": "Haber-Bosch (Process)",
    "HD": "Heavy Duty",
    "HDV": "Heavy Duty Vehicle",
    "hef": "High Efficiency Furnace",
    "HFO": "Heavy Fuel Oil",
    "hwod": "Hot Water On Demand",
    "hwt": "Hot Water Tank",
    "ICB": "Inter-city Bus",
    "ICE": "Internal Combustion Engine",
    "icemd": "Machine Drive Powered by Internal Combustion Engine",
    "icepg": "Power Generation via Internal Combustion Engine",
    "j": "Jet Fuel",
    "jr": "Renewable Jet Fuel",
    "LCOH": "Levelized Cost of Hydrogen",
    "LDV": "Light Duty Vehicle",
    "LFO": "Light Fuel Oil",
    "LH2": "Liquid Hydrogen",
    "LNG": "Liquified Natural Gas",
    "Km": "Kilometer",
    "M": "Agriculture Motive",
    "Mar.": "Marine",
    "MDV": "Medium Duty vehicle",
    "MSW": "Municipal Solid Waste",
    "N2O": "Nitrogen Oxide",
    "NG": "Natural Gas",
    "ngCS": "Natural Gas with Carbon Capture and Storage",
    "ngr": "Renewable Natural Gas",
    "NH3": "Ammonia",
    "Nm": "Agriculture Non Motive",
    "NZ": "Net-zero",
    "NZEST": "Net-zero Energy System Transition",
    "OEM": "Original Equipment Manufacture",
    "Off R.": "Off Road",
    "op": "Other Processes",
    "OPEX": "Operational Expenditure",
    "othblg": "other uses of Elec in buildings (lights, plugs)",
    "p": "Gasoline",
    "ph": "Process Heat",
    "PJ": "Petajoule",
    "pr": "Renewable Petroleum",
    "pro": "Prop",
    "PV": "Solar Photovoltaic",
    "P & P": "Pulp and Paper Industry",
    "resht": "Resistant Heat",
    "Res.": "Residential",
    "RLF": "Renewable Liquid Fuels",
    "ROth": "Residential Other Applications",
    "RWH": "Residential Water Heating",
    "SAGD": "Steam Assisted Gravity Drainage",
    "SB": "School Bus",
    "Smelt": "Smelting Industry",
    "solarw": "Solar Hot Water",
    "SQ": "Status Quo",
    "st": "Steam",
    "TRL": "Technology Readiness Level",
    "TT": "Tube Trailer",
    "TWh": "Terawatt hours",
    "UB": "Urban Transit Bus",
    "VKT": "Vehicle kms Travelled",
    "w": "Wood",
    "pl": "Petroleum Based Plastics",
    "WCSB": "Western Canadian Sedimentary Basin"
}

Province_real = {
    "ab" : "Alberta",
    "qc" : "Quebec",
    "sk" : "Sasktchewan",
    "atl" : "Atlantic Provinces",
    "bct" : "British-Columbia",
    "on" : "Ontario",
    "mb": "Manitoba"
    
}


carrier_dict = {
    "d": "Diesel",
    "db": "Biodiesel",
    "dr": "R-Diesel",
    "et": "Ethanol",
    "j": "Jet Fuel",
    "p": "Gasoline",
    "e": "Elec",
    "hfo": "HFO",
    "lfo": "LFO",
    "ng": "NG",
    "pro": "Prop",
    "st": "Steam",
    "c": "Coal",
    "pl": "Plastics",
    "w": "Wood"
}


# === Function to process Status-Quo scenario CSV ===
def process_SQ(input_csv_path, output_csv_path):
    """
    Process Status-Quo scenario CSV:
    - Loads raw CSV from input_csv_path
    - Transforms wide data (years 2000-2050) into long format
    - Maps codes to descriptive names using predefined dictionaries
    - Writes cleaned data to output_csv_path
    """
    # Load Status-Quo scenario data into a DataFrame
    df_SQ = pd.read_csv(input_csv_path)

    # Melt the DataFrame from wide to long format
    df_SQ = df_SQ.melt(
        id_vars=["prov","Sector","Subsector","en_carrier","tech"],
        value_vars=[str(y) for y in range(2000, 2051)],
        var_name="Year",
        value_name="Energy demand (PJ/yr)"
    )

    # Map codes to descriptive names
    df_SQ["Carrier"] = df_SQ["en_carrier"].map(carrier_dict)
    df_SQ["Tech_name"] = df_SQ["tech"].map(carrier_tech_dict)
    df_SQ["Tech_subsector"] = df_SQ["Subsector"].map(sector_activity_dict)
    df_SQ["Province"] = df_SQ["prov"].map(Province_real)
    
    Path_Carbon_Content = "Carbon_Content.csv"
    df_CC = pd.read_csv(Path_Carbon_Content)


    df_merged = df_SQ.merge(df_CC, on="Carrier", how='left')
    df_merged['Carbon Content MT c'] = df_merged['Energy demand (PJ/yr)'] / df_merged['Energy per kg C (MJ/kgC)'] 

    # Export the transformed data to CSV
    df_merged.to_csv(output_csv_path, index=False)


# Optional: Script execution guard for standalone usage
if __name__ == "__main__":
    # Example usage with default paths
    excel_files_SQ = "/Users/antoineduplantie-grenier/Desktop/Modeling/VIZ/Output/Status-quo scenario data.csv"
    output_path = "/Users/antoineduplantie-grenier/Desktop/Modeling/VIZ/SQ_Post_Process.csv"
    process_SQ(excel_files_SQ, output_path)
