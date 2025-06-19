
PAGES = {
    "Intro": "intro",
    "Energy Demand": "Energy_Demand",
    "Energy Demand Grouped": "Energy_Demand_Grouped",
    # "Pie Chart All Sectors": "page_2",
    "Pie Chart Agriculture": "page_3",
    "Pie Chart Transport": "page_4",
    "Pie Chart Building": "page_5",
    "Pie Chart Industry": "page_6",
    "Energy Demand (Bar Chart)": "Energy_Demand_Bar",
    "Carbon Content (Bar Chart)": "Carbon_content_Bar",
    "Multi Sector Bar Chart": "Multi_Sector_Bar",
    "Industry Subsector Bar Chart": "Industry_Sector_Bar",
    "Grouped Industry Bar Chart": "Grouped_Industry_Bar",
    "GHG Emissions": "GHG_Graph",
}

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
    "Alum_fs": "Alum_fs",
    "Alum_md": "Alum_md",
    "Alum_op": "Alum_op",
    "Alum_ph": "Alum_ph",
    "Alum_tr": "Alum_tr",
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
    "K mine_fs": "K mine_fs",
    "K mine_md": "K mine_md",
    "K mine_ph": "K mine_ph",
    "K mine_tr": "K mine_tr"
}


carrier_dict = {
    "d":   "Diesel",
    "db":  "Biodiesel",
    "dr":  "R-Diesel",
    "et":  "Ethanol",
    "j":   "Jet Fuel",
    "p":   "Gasoline",
    "e":   "Elec",
    "hfo": "HFO",
    "lfo": "LFO",
    "ng":  "NG",
    "pro": "Prop",
    "st":  "Steam",
    "c":   "Coal",
    "pl":  "Plastics",
    "w":   "Wood"
}


carrier_colors = {
    # Fossil liquids
    "Diesel":    "#800100",
    "R-Diesel":  "#82ec7e",   # Renewable / drop‑in diesel
    "Biodiesel": "#29C12E",
    "Gasoline":  "#ff0000",
    "Jet Fuel":  "#ffa6a7",
    "HFO":       "#4C4A4A",   # Heavy fuel‑oil (bunker)
    "LFO":       "#9e9e9e",   # Light fuel‑oil
    # Gaseous & thermal
    "Prop":      "#4A7FC8",
    "NG":  "#4f95d9",
    "Steam":        "#b3e5fc",
    # Low‑carbon / renewables
    "Ethanol":   "#87DA78",
    "Wood":      "#02b050",
    "Plastics":  "#65514b",
    "Elec": "#ffbf00",
    # Solids
    "Coal": "#0d0d0d"
}

sector_activity_colors = {
    # Cement (yellow gradient)
    "Cement_fs": "#bca136",
    "Cement_md": "#c6b354",
    "Cement_op": "#d1c672",
    "Cement_ph": "#dbd890",
    "Cement_tr": "#e5ebb0",
    # Chemical Industry (blue gradient)
    "Chem_fs": "#2986cc",
    "Chem_md": "#52a2d9",
    "Chem_op": "#7abde6",
    "Chem_pg": "#a3d9f2",
    "Chem_ph": "#ccf5ff",
    "Chem_tr": "#e6faff",
    # Construction (orange/gold gradient)
    "Const_pg": "#bf9000",
    "Const_ph": "#c8a536",
    "Const_tr": "#d2bb6d",
    # Copper Mine (brown/copper gradient)
    "Cu mine_fs": "#b45f06",
    "Cu mine_md": "#c17328",
    "Cu mine_op": "#cd8750",
    "Cu mine_ph": "#da9b77",
    "Cu mine_pg": "#e6af9e",
    "Cu mine_tr": "#f3c3c6",
    # Forest Products (forest green gradient)
    "Forest_pg": "#3c763d",
    "Forest_ph": "#74a874",
    "Forest_tr": "#adcbb0",
    # Iron & Steel (grey gradient)
    "I&S_fs": "#808080",
    "I&S_md": "#999999",
    "I&S_op": "#b3b3b3",
    "I&S_pg": "#cccccc",
    "I&S_ph": "#e5e5e5",
    "I&S_tr": "#f2f2f2",
    # Manufacturing (light green gradient)
    "Manuf_fs": "#b6d7a8",
    "Manuf_md": "#c5dfbc",
    "Manuf_op": "#d5e8cf",
    "Manuf_pg": "#e4f0e3",
    "Manuf_ph": "#f3f8f7",
    "Manuf_tr": "#ffffff",
    # Other Non-Metal (purple gradient)
    "O non-met_fs": "#674ea7",
    "O non-met_md": "#8b7ec1",
    "O non-met_pg": "#afaeda",
    "O non-met_ph": "#d3cff2",
    "O non-met_tr": "#f7f7ff",
    # Salt (pale teal gradient)
    "Salt_fs": "#a2c4c9",
    "Salt_md": "#bad2d7",
    "Salt_ph": "#d3e1e5",
    "Salt_tr": "#ebf0f3",
    # Smelting (orange gradient)
    "Smelt_fs": "#e69138",
    "Smelt_md": "#eaad69",
    "Smelt_op": "#efd999",
    "Smelt_ph": "#f2e4c3",
    "Smelt_tr": "#f7f3ed",
    # Pulp & Paper (green gradient)
    "p&p_fs": "#6aa84f",
    "p&p_md": "#93bc7e",
    "p&p_op": "#bad0ad",
    "p&p_pg": "#e1e4dc",
    "p&p_ph": "#f8f9f7",
    "p&p_tr": "#ffffff",
    # Aluminum (blue gradient)
    "Alum_fs": "#a4c2f4",
    "Alum_md": "#b7d1f7",
    "Alum_op": "#cae1fa",
    "Alum_ph": "#ddefff",
    "Alum_tr": "#f0fcff",
    # Gold & Silver Mine (gold/yellow gradient)
    "G&S mine_fs": "#ffd966",
    "G&S mine_md": "#ffe391",
    "G&S mine_op": "#ffedbd",
    "G&S mine_pg": "#fff8e8",
    "G&S mine_ph": "#ffffff",
    "G&S mine_tr": "#fffdf5",
    # Iron Mine (blue-grey gradient)
    "I mine_fs": "#6fa8dc",
    "I mine_md": "#97bee4",
    "I mine_op": "#bfd5ec",
    "I mine_pg": "#e7ebf3",
    "I mine_ph": "#f3f8fb",
    "I mine_tr": "#ffffff",
    # Other Metal (peach/tan gradient)
    "O metal_fs": "#f6b26b",
    "O metal_md": "#f8c693",
    "O metal_op": "#f9d8bc",
    "O metal_pg": "#faebdc",
    "O metal_ph": "#fcfcf5",
    "O metal_tr": "#ffffff",
    # Potash Mine (rose/lavender gradient)
    "K mine_fs": "#c27ba0",
    "K mine_md": "#d6a4be",
    "K mine_ph": "#ebcee0",
    "K mine_tr": "#fff7fa",
    # Transportation/other sector codes (assign greys or vivid distincts)
    "Mot": "#555555",
    "Nmot": "#888888",
    "COth": "#bbbbbb",
    "CSH": "#666ee0",
    "CWH": "#a64d79",
    "ROth": "#999999",
    "RSH": "#b7b7b7",
    "RWH": "#cccccc",
    "Air": "#2b78e4",
    "HDV": "#134f5c",
    "ICB": "#741b47",
    "LDV": "#bf9000",
    "MDV": "#f6b26b",
    "Off-Road": "#cfe2f3",
    "Rail": "#b45f06",
    "SB": "#6d9eeb",
    "UB": "#38761d",
    "Marine": "#1155cc"
}

carrier_tech_colors = {
    # Diesel (deep red to pink)
    "d_ice": "#800100",
    "d_icemd": "#a32e23",
    "d_icepg": "#c65b46",
    "d_ph": "#e8886a",
    # Biodiesel (bright green)
    "db_ice": "#29C12E",
    # Renewable Diesel (pastel green)
    "dr_ice": "#82ec7e",
    # Ethanol (olive green)
    "et_ice": "#5A7B39",
    # Jet Fuel (pale salmon)
    "j_ice": "#ffa6a7",
    # Gasoline (bright red)
    "p_ice": "#ff0000",
    # Elec (yellow/orange)
    "e_resht": "#ffbf00",
    "e_othbldg": "#ffd966",
    "e_hwt": "#fff2b2",
    "e_fs": "#ffdd69",
    "e_gridmd": "#ffe9a3",
    "e_op": "#fff6d1",
    "e_bev": "#fffde4",
    "e_ashp": "#ffe184",
    # HFO (medium grey scale)
    "hfo_boil": "#757575",
    "hfo_othbldg": "#979797",
    "hfo_hwt": "#b9b9b9",
    "hfo_ph": "#dbdbdb",
    "hfo_icepg": "#ededed",
    "hfo_ice": "#cacaca",
    # LFO (light grey scale)
    "lfo_boil": "#9e9e9e",
    "lfo_othbldg": "#bdbdbd",
    "lfo_hwt": "#dcdcdc",
    "lfo_cook": "#ebebeb",
    "lfo_hef": "#c5c5c5",
    "lfo_mef": "#d6d6d6",
    "lfo_nef": "#e7e7e7",
    # NG (blue gradient)
    "ng_mef": "#4f95d9",
    "ng_cook": "#71aee1",
    "ng_boil": "#92c7e9",
    "ng_hwt": "#b4e0f1",
    "ng_icemd": "#d5f9f9",
    "ng_ph": "#a4caf7",
    "ng_icepg": "#c5ddfb",
    "ng_hef": "#c5ebfa",
    "ng_nef": "#e0f2fa",
    "ng_ice": "#b1d8f8",
    # Prop (mid-blue gradient)
    "pro_mef": "#043CD6",
    "pro_cook": "#356de4",
    "pro_boil": "#6e9ef0",
    "pro_hwt": "#b2d0fb",
    "pro_ice": "#dbe9fd",
    # Steam (light blue gradient)
    "st_HtXch": "#b3e5fc",
    "st_othbldg": "#c7ebfb",
    "st_hwt": "#dbf2fb",
    "st_ph": "#eaf8fc",
    "st_htXch": "#f7fcff",
    # Coal (black)
    "c_ph": "#0d0d0d",
    # Plastics (brownish)
    "pl_ph": "#65514b",
    # Wood (forest green gradient)
    "w_ph": "#02b050",
    "w_cook": "#5ed075",
    "w_stove": "#99e0a1",
    "w_hwt": "#b6ebbf",
}



stack_order = [
    # Fossil & petrochemical first (bottom of stacks)
    "Coal",
    "Plastics",
    "HFO",
    "LFO",
    "Diesel",
    "Gasoline",
    "Jet Fuel",
    "Prop",
    "NG",
    "Steam",
    "Biodiesel",
    "R-Diesel",
    #"PR" att zero but will be added at one point or in NZ
    "Ethanol",
    "Wood",
    "Elec"
]

category_mapping = {
    "Cement": [
        "Cement_fs",  # Cement Facility Support
        "Cement_md",  # Cement Machine Drive
        "Cement_op",  # Cement Other Processes
        "Cement_ph",  # Cement Process Heat
        "Cement_tr"   # Cement Transport
    ],
    "Chemical Industry": [
        "Chem_fs",  # Chemical Industry Facility Support
        "Chem_md",  # Chemical Industry Machine Drive
        "Chem_op",  # Chemical Industry Other Processes
        "Chem_pg",  # Chemical Industry Power Generation
        "Chem_ph",  # Chemical Industry Process Heat
        "Chem_tr"   # Chemical Industry Transport
    ],
    "Construction": [
        "Const_pg",  # Construction Power Generation
        "Const_ph",  # Construction Process Heat
        "Const_tr"   # Construction Transport
    ],
    "Copper Mine": [
        "Cu mine_fs",  # Copper Mine Facility Support
        "Cu mine_md",  # Copper Mine Machine Drive
        "Cu mine_op",  # Copper Mine Other Processes
        "Cu mine_ph",  # Copper Mine Process Heat
        "Cu mine_pg",  # Copper Mine Power Generation
        "Cu mine_tr"   # Copper Mine Transport
    ],
    "Forest Products": [
        "Forest_pg",  # Forest Products Power Generation
        "Forest_ph"   # Forest Products Process Heat
    ],
    "Iron and Steel": [
        "I&S_fs",  # Iron and Steel Facility Support
        "I&S_md",  # Iron and Steel Machine Drive
        "I&S_op",  # Iron and Steel Other Processes
        "I&S_pg",  # Iron and Steel Power Generation
        "I&S_ph",  # Iron and Steel Process Heat
        "I&S_tr"   # Iron and Steel Transport
    ],
    "Manufacturing": [
        "Manuf_fs",  # Manufacturing Facility Support
        "Manuf_md",  # Manufacturing Machine Drive
        "Manuf_op",  # Manufacturing Other Processes
        "Manuf_pg",  # Manufacturing Power Generation
        "Manuf_ph",  # Manufacturing Process Heat
        "Manuf_tr"   # Manufacturing Transport
    ],
    "Other Non-Metal": [
        "O non-met_fs",  # Other Non-Metal Facility Support
        "O non-met_md",  # Other Non-Metal Machine Drive
        "O non-met_pg",  # Other Non-Metal Power Generation
        "O non-met_ph",  # Other Non-Metal Process Heat
        "O non-met_tr"   # Other Non-Metal Transport
    ],
    "Salt": [
        "Salt_fs",  # Salt Facility Support
        "Salt_md",  # Salt Machine Drive
        "Salt_ph",  # Salt Process Heat
        "Salt_tr"   # Salt Transport
    ],
    "Smelting": [
        "Smelt_fs",  # Smelting Industry Facility Support
        "Smelt_md",  # Smelting Industry Machine Drive
        "Smelt_op",  # Smelting Industry Other Processes
        "Smelt_ph",  # Smelting Industry Process Heat
        "Smelt_tr"   # Smelting Industry Transport
    ],
    "Pulp and Paper": [
        "p&p_fs",  # Pulp and Paper Industry Facility Support
        "p&p_md",  # Pulp and Paper Industry Machine Drive
        "p&p_op",  # Pulp and Paper Industry Other Processes
        "p&p_pg",  # Pulp and Paper Industry Power Generation
        "p&p_ph",  # Pulp and Paper Industry Process Heat
        "p&p_tr"   # Pulp and Paper Industry Transport
    ],
    "Aluminum": [
        "Alum_fs",  # Aluminum Facility Support
        "Alum_md",  # Aluminum Machine Drive
        "Alum_op",  # Aluminum Other Processes
        "Alum_ph",  # Aluminum Process Heat
        "Alum_tr"   # Aluminum Transport
    ],
    "Gold and Silver Mine": [
        "G&S mine_fs",  # Gold and Silver Mine Facility Support
        "G&S mine_md",  # Gold and Silver Mine Machine Drive
        "G&S mine_op",  # Gold and Silver Mine Other Processes
        "G&S mine_pg",  # Gold and Silver Mine Power Generation
        "G&S mine_ph",  # Gold and Silver Mine Process Heat
        "G&S mine_tr"   # Gold and Silver Mine Transport
    ],
    "Iron Mine": [
        "I mine_fs",  # Iron Mine Facility Support
        "I mine_md",  # Iron Mine Machine Drive
        "I mine_op",  # Iron Mine Other Processes
        "I mine_pg",  # Iron Mine Power Generation
        "I mine_ph",  # Iron Mine Process Heat
        "I mine_tr"   # Iron Mine Transport
    ],
    "Other Metal": [
        "O metal_fs",  # Other Metal Facility Support
        "O metal_md",  # Other Metal Machine Drive
        "O metal_op",  # Other Metal Other Processes
        "O metal_pg",  # Other Metal Power Generation
        "O metal_ph",  # Other Metal Process Heat
        "O metal_tr"   # Other Metal Transport
    ],
    "Potash Mine": [
        "K mine_fs",  # Potash Mine Facility Support
        "K mine_md",  # Potash Mine Machine Drive
        "K mine_ph",  # Potash Mine Process Heat
        "K mine_tr"   # Potash Mine Transport
    ]
}

group_colors = {
"Transport": "#54AA45",
"Building": "#8ED0F2",
"Industry": "#C974C7"   
}


group_order = ["Transport", "Building", "Industry"]
fossil_carriers = ["Coal", "HFO", "LFO",
                    "Diesel", "R-Diesel", "Gasoline", "Jet Fuel",
                    "Prop", "NG", "Plastics"]



tech_subsector_to_group = {}
# Manufacturing
manufacturing_list = [
    "Alum_fs", "Alum_md", "Alum_op", "Alum_ph", "Alum_tr",
    "Cement_fs", "Cement_md", "Cement_op", "Cement_ph", "Cement_tr",
    "Chem_fs", "Chem_md", "Chem_op", "Chem_pg", "Chem_ph", "Chem_tr",
    "Const_pg", "Const_ph", "Const_tr",
    "I&S_fs", "I&S_md", "I&S_op", "I&S_pg", "I&S_ph", "I&S_tr",
    "Manuf_fs", "Manuf_md", "Manuf_op", "Manuf_pg", "Manuf_ph", "Manuf_tr",
    "Smelt_fs", "Smelt_md", "Smelt_op", "Smelt_ph", "Smelt_tr",
    "p&p_fs", "p&p_md", "p&p_op", "p&p_pg", "p&p_ph", "p&p_tr"
]
for code in manufacturing_list:
    tech_subsector_to_group[code] = "Manufacturing"
# Extractive Industry
extractive_list = [
    "Cu mine_fs", "Cu mine_md", "Cu mine_op", "Cu mine_pg", "Cu mine_ph", "Cu mine_tr",
    "Forest_pg", "Forest_ph", "Forest_tr",
    "G&S mine_fs", "G&S mine_md", "G&S mine_op", "G&S mine_pg", "G&S mine_ph", "G&S mine_tr",
    "I mine_fs", "I mine_md", "I mine_op", "I mine_pg", "I mine_ph", "I mine_tr",
    "O non-met_md", "O non-met_pg", "O non-met_tr",
    "K mine_fs", "K mine_md", "K mine_ph", "K mine_tr",
    "O metal_fs", "O metal_md", "O metal_op", "O metal_pg", "O metal_ph", "O metal_tr",
    "O non-met_fs", "O non-met_ph",
    "Salt_fs", "Salt_md", "Salt_ph", "Salt_tr"
]
for code in extractive_list:
    tech_subsector_to_group[code] = "Extractive Industry"