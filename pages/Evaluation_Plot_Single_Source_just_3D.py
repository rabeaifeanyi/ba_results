import pandas as pd # type: ignore
import plotly.express as px # type: ignore
import streamlit as st # type: ignore
import os
import re
from collections import defaultdict
from pathlib import Path

# CMAPS: https://plotly.com/python/builtin-colorscales/

def plot_3d(df, title, param, cmap, color_range=None):
    fig = px.scatter_3d(
        x=df["real_x"],
        y=df["real_z"],
        z=df["real_y"], 
        hover_name=df["name"],
        color=df[param], 
        color_continuous_scale=cmap,
        range_color=color_range
    )
    fig.update_traces(marker={'size': 5})
    fig.update_layout(
        scene=dict(
            xaxis=dict(title="Width (x)"),
            yaxis=dict(title="Distance (z)"), 
            zaxis=dict(title="Height (y)")
        ),
        margin=dict(l=0, r=0, b=0, t=40),
        coloraxis_colorbar_title_text = title
    )
    return fig

def plot_2d(df, title, param, cmap, color_range=None):
    fig = px.scatter(
        x=df["real_x"],
        y=df["real_y"], 
        hover_name=df["name"],
        color=df[param], 
        color_continuous_scale=cmap,
        range_color=color_range
    )
    fig.update_traces(marker={'size': 10})
    fig.update_layout(
        xaxis=dict(title="X-Axis"),
        yaxis=dict(title="Y-Axis"),
        margin=dict(l=0, r=0, b=0, t=40),
        coloraxis_colorbar_title_text = title
    )
    return fig

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

def get_parameter_description(category, distance=None, axis=None):
    descriptions = {
        "Accuracy": (
            f"Accuracy represents the proportion of predictions that are within {distance} cm of the real coordinates. "
            f"It is calculated as the fraction of distances (dist_to_real_coord) that are less than or equal to {distance} cm, "
            f"normalized by the total number of predictions. Specifically: \n"
            f"Accuracy = (Number of distances <= {distance}) / Total Number of Predictions."
        ),
        "Beamforming Maxima": (
            "Beamforming Maxima measures the Euclidean distance between the real coordinates (real_x, real_y, real_z) "
            "and the maximum of the beamforming output (beamforming_max_x, beamforming_max_y, beamforming_max_z). "
            "It is computed as: \n"
            "Beamforming Maxima = sqrt((real_x - beamforming_max_x)^2 + (real_y - beamforming_max_y)^2 + (real_z - beamforming_max_z)^2)."
        ),
        "Interquartile Range": (
            "The Interquartile Range (IQR) is the difference between the 75th and 25th percentiles of the distances "
            "to the real coordinates (dist_to_real_coord). It is computed as: \n"
            "IQR = 75th Percentile - 25th Percentile."
        ),
        "Mean Absolute Error": (
            "The Mean Absolute Error (MAE) is the average of the absolute differences between the estimated coordinates "
            "and the real coordinates. For 3D coordinates, it is computed as: \n"
            "MAE = (|avg_x_t - real_x| + |avg_y_t - real_y| + |avg_z_t - real_z|) / 3."
        ),
        "Mean Difference": (
            f"Mean Difference along the {axis}-axis represents the average absolute difference between the estimated "
            f"and real values along the {axis}-axis. It is calculated as: \n"
            f"Mean Difference = Mean(|avg_{axis}_t - real_{axis}|)."
        ),
        "Mean Distance": (
            "Mean Distance is the average Euclidean distance between the estimated coordinates "
            "and the real coordinates. It is computed as: \n"
            "Mean Distance = Mean(sqrt((avg_x_t - real_x)^2 + (avg_y_t - real_y)^2 + (avg_z_t - real_z)^2))."
        ),
        "Median Distance": (
            "Median Distance is the median of the Euclidean distances between the estimated coordinates "
            "and the real coordinates. The distance is calculated as: \n"
            "d = sqrt((avg_x_t - real_x)^2 + (avg_y_t - real_y)^2 + (avg_z_t - real_z)^2)."
        ),
        "Standard Deviation": (
            "Standard Deviation measures the spread of the estimated coordinates around the real coordinates. "
            "It is computed as the average of the standard deviations along all axes: \n"
            "Standard Deviation = (std_x + std_y + std_z) / 3."
        ),
    }
    return descriptions.get(category, "No description available for this category.")

def main():
    st.set_page_config(layout="wide")
    
    st.sidebar.subheader("Model Parameters")
    
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

    st.sidebar.subheader("Evaluation Settings")
    category = st.sidebar.selectbox(
        "Select Parameter to analyse",
        ["Accuracy", "Beamforming Maxima", "Interquartile Range", "Mean Absolute Error", 
        "Mean Difference", "Mean Distance", "Median Distance", "Standard Deviation"]
    )
    
    only_xy = st.sidebar.checkbox("Only x and y values", key="ignore_z")

    if category == "Accuracy":
        distance = st.sidebar.selectbox("Select Distance (cm)", [5, 10, 15, 20, 30, 40, 50, 60])
        param_3d = f"accuracy_{distance}cm_xy" if only_xy else f"accuracy_{distance}cm"
        color_range = [0, 1]
    elif category == "Beamforming Maxima":
        param_3d = "beamforming_dist_xy" if only_xy else "beamforming_dist"
        color_range = [0, df["beamforming_dist"].max()]
    elif category == "Interquartile Range":
        param_3d = "iqr_dist"  # Hier gibt es keine Unterscheidung für xy
        color_range = [0, df["iqr_dist"].max()]
    elif category == "Mean Absolute Error":
        param_3d = "mae_xy" if only_xy else "mae_coord"
        color_range = [0, df["mae_coord"].max()]
    elif category == "Mean Difference":
        axis = st.sidebar.selectbox("Select Axis", ["x", "y", "z"])
        param_3d = f"mean_diff_{axis}"  # Keine Unterscheidung für xy hier
        color_range = [0, df[f"mean_diff_{axis}"].max()]
    elif category == "Mean Distance":
        param_3d = "mean_dist_xy" if only_xy else "mean_dist"
        color_range = [0, df["mean_dist"].max()]
    elif category == "Median Distance":
        param_3d = "median_dist_xy" if only_xy else "median_dist"
        color_range = [0, df["median_dist"].max()]
    elif category == "Standard Deviation":
        param_3d = "coord_std_xy" if only_xy else "coord_std"
        color_range = [df[param_3d].min(), df[param_3d].max()]
    else:
        st.error("Unknown category selected.")
        return
    
    cmap = st.sidebar.selectbox("Choose Color Map", ["amp", "Viridis", "Blues", "deep"])

    st.markdown(f"### {category}")
    description = get_parameter_description(category, distance=distance if category == "Accuracy" else None, axis=axis if category == "Mean Difference" else None)
    st.markdown(f"{description}") 

    fig_3d = plot_3d(df, f"{param_3d}", param_3d, cmap, color_range)
    st.plotly_chart(fig_3d, use_container_width=True)
    
        

if __name__ == "__main__":
    main()
