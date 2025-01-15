import streamlit as st #type: ignore
import os
import re
from pathlib import Path
from collections import defaultdict
import pandas as pd #type: ignore
import plotly.express as px #type: ignore

def extract_parameters_from_paths(results_dir):
    parameter_combinations = defaultdict(set)
    files = [f for f in os.listdir(results_dir) if f.endswith(".csv")]
    
    for file in files:
        match = re.search(r"f(\d+)_bs(\d+)_nob(\d+)", file)
        if match:
            frequency, blocksize, nob = match.groups()
            parameter_combinations["frequency"].add(int(frequency))
            parameter_combinations["blocksize"].add(int(blocksize))
            parameter_combinations["nob"].add(int(nob))
    
    return {k: sorted(v) for k, v in parameter_combinations.items()}

def filter_valid_combinations(selected_frequency, selected_blocksize, results_dir):
    valid_nob = set()
    files = [f for f in os.listdir(results_dir) if f.endswith(".csv")]
    
    for file in files:
        match = re.search(r"f(\d+)_bs(\d+)_nob(\d+)", file)
        if match:
            frequency, blocksize, nob = match.groups()
            if int(frequency) == selected_frequency and int(blocksize) == selected_blocksize:
                valid_nob.add(int(nob))
    
    return sorted(valid_nob)


def main():
    st.set_page_config(layout="wide")

    st.sidebar.header("Settings")
    
    results_dir = "results"
    parameter_combinations = extract_parameters_from_paths(results_dir)
    
    selected_frequency = st.sidebar.selectbox("Select Frequency (Hz)", parameter_combinations["frequency"])
    selected_blocksize = st.sidebar.selectbox("Select Blocksize", parameter_combinations["blocksize"])
    valid_nob = filter_valid_combinations(selected_frequency, selected_blocksize, results_dir)
    selected_nob = st.sidebar.selectbox("Select Number of Blocks", valid_nob if valid_nob else ["No valid combinations"])
    
    file = f"result_summary_f{selected_frequency}_bs{selected_blocksize}_nob{selected_nob}.csv"
    
    if valid_nob:
        pass
    else:
        st.sidebar.warning(f"No valid combinations for the selected Frequency and Blocksize.")
        return

    df = pd.read_csv(Path(results_dir, file))
    
    df["Index"] = range(1, len(df) + 1)
    
    # Filteroptionen hinzufügen (optional)
    st.subheader("Plot a Parameter")
    x_axis = st.selectbox("Select X-Axis", options=["name"] + list(df.columns), index=0)
    y_axis = st.selectbox("Select Y-Axis", options=["None"] + list(df.columns), index=0)

    if x_axis != "None" and y_axis != "None":
        # Plot erstellen
        fig = px.scatter(
            df,
            x=x_axis,
            y=y_axis,
            title=f"Scatter Plot: {x_axis} vs {y_axis}",
            labels={x_axis: x_axis, y_axis: y_axis},
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Please select both X and Y axes to generate a plot.")



    
if __name__ == "__main__":
    main()