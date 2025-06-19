# NZEST Explorator Dashboard

Interactive Streamlit dashboard for NZEST Status-Quo energy demand projections.

---

## Table of Contents

1. **Project Overview**  
2. **Prerequisites**  
3. **Installation**  
4. **Running the App**  
5. **Environment Variables & Configuration**  
6. **Code Structure**  
   - **1. Imports**  
   - **2. Helper Functions**  
   - **3. Page Setup (`setup_page`)**  
   - **4. Intro Screen (`Intro`)**  
   - **5. Main App Runner (`run_app`)**  
   - **6. Plot Modules (`Plot/`)**  
7. **Extending & Customizing**  
8. **License**  

---

## Project Overview

This repository hosts a Streamlit-based dashboard that visualizes energy-demand projections from the NZEST model under the **Status-Quo** scenario.

Key features:
- **Time series** and **bar charts** of energy demand by sector.  
- **Pie charts** for sectoral breakdowns.  
- **GHG emissions** visualizations.  
- Downloadable data via sidebar controls.

---

## Prerequisites

- **Python** ≥ 3.8  
- **Git**  
- A virtual environment tool (e.g., `venv`, `conda`)

---

## Installation

1. **Clone the repository**  
   ```bash
   git clone https://github.com/YourOrg/NZEST_SQ.git
   cd NZEST_SQ
   ```

2. **Create & activate a virtual environment**  
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate      # macOS/Linux
   .\.venv\Scripts\activate    # Windows
   ```

3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

---

## Running the App

In the project root directory, run:

```bash
streamlit run nzest_explorator_v4.py
```

This launches the dashboard at `http://localhost:8501`.

---

## Environment Variables & Configuration

- No external API keys required.  
- Data and assets should reside in the `Input/` folder:
  ```
  NZEST_SQ/
  ├── Input/
  │   └── logo.png
  ├── nzest_explorator_v4.py
  └── Plot/
      └── ...plot modules...
  ```
- If your structure differs, adjust `base_dir` logic in `setup_page()`.

---

## Code Structure

### 1. Imports

```python
# Standard library
import os
from pathlib import Path
from collections import defaultdict

# Third-party
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Local modules
from nzest_constants import (...)
from Plot.Energy_Demand import Energy_Demand
# ... other Plot imports ...
```

### 2. Helper Functions

- **`load_logo()`**: Resolves and displays `Input/logo.png` in the sidebar.  
- **`_handle_continue()`**: Marks intro as shown and navigates to the main dashboard.

### 3. Page Setup (`setup_page`)

Encapsulates Streamlit setup:

```python
def setup_page():
    st.set_page_config(...)
    st.markdown(...fade-in CSS...)
    st.markdown(...sidebar CSS...)
    load_logo()
    # Initialize session_state
```

### 4. Intro Screen (`Intro`)

Renders the welcome page with a “Continue” button:

```python
def Intro():
    st.markdown(...hide sidebar...)
    st.image(...)
    st.title(...)
    st.button("Continue", on_click=_handle_continue)
    st.stop()
```

### 5. Main App Runner (`run_app`)

Orchestrates the application flow:

```python
def run_app():
    setup_page()
    if not st.session_state["intro_shown"]:
        Intro()
    pages = [k for k in PAGES if k != "Intro"]
    selection = st.sidebar.selectbox("Go to", pages)
    PAGES.get(selection)()
```

### 6. Plot Modules (`Plot/`)

Each file in `Plot/` defines a function/class to render a specific chart (e.g., `Energy_Demand.py`, `GHG_Graph.py`, etc.).

---

## Extending & Customizing

- **Add pages**: Create new plot modules, import them, and register in `PAGES` within `nzest_constants.py`.  
- **Styling**: Tweak CSS injections in `setup_page()`.  
- **Data sources**: Update constants and Plot modules to load additional datasets.

---

