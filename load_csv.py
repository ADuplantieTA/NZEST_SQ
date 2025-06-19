import streamlit as st
import pandas as pd

from nzest_constants import (
    carrier_dict,

)

@st.cache_data
def load_csv(path) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False)
    df.columns = df.columns.str.strip()
    col_map = {}
    # Map Province, Year, Sector
    for orig, name in [(c, 'Province') for c in df.columns if c.lower()=='province'] + \
                       [(c, 'Year') for c in df.columns if c.lower()=='year'] + \
                       [(c, 'Sector') for c in df.columns if c.lower()=='sector']:
        col_map[orig] = name
    # Energy demand (detect unit)
    ed_cols = [c for c in df.columns if 'energy demand' in c.lower()]
    if ed_cols:
        orig = ed_cols[0]
        unit = 'PJ' if 'pj' in orig.lower() else 'GJ'
        col_map[orig] = f'Energy ({unit}/yr)'
    # Carrier
    carr = [c for c in df.columns if c.lower() in ['carrier','carrier group']]
    if carr:
        col_map[carr[0]] = 'Carrier'
    # Tech_name, Tech_subsector
    for target in ['Tech_name','Tech_subsector']:
        cols = [c for c in df.columns if c.lower().replace(' ','_')==target.lower()]
        if cols:
            col_map[cols[0]] = target

    # Apply the column renaming
    df = df.rename(columns=col_map)

    # Convert carrier short codes to full names if present
    if 'Carrier' in df.columns:
        df['Carrier'] = (
            df['Carrier']
            .astype(str)
            .str.lower()
            .map(carrier_dict)
            .fillna(df['Carrier'])
        )

    return df