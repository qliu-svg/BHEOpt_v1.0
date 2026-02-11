"""
Created on Wed Feb 11 10:21:54 2026

@author: qliu
"""

import streamlit as st
from PIL import Image
import numpy as np
import pandas as pd
import folium
from streamlit_folium import st_folium
from main_refactor import plot_initial_heatmap, run_optimization, plot_optimized_heatmap
from pyproj import Transformer
import plotly.express as px

st.markdown("""
    <style>
    .block-container {
        max-width: 1000px;
        margin: auto;
        padding-left: 2rem;
        padding-right: 2rem;
        text-align: left;
    }
    h1, h2, h3, h4, h5, h6, p {
        text-align: left !important;
    }
    [data-testid="stSidebar"] {
        width: 460px !important;
        min-width: 300px !important;
        max-width: 500px !important;
    }
    </style>
""", unsafe_allow_html=True)

if "show_initial_plot" not in st.session_state:
    st.session_state["show_initial_plot"] = False
if "show_opt_plot" not in st.session_state:
    st.session_state["show_opt_plot"] = False
if "optimized_q" not in st.session_state:
    st.session_state["optimized_q"] = None

logo = Image.open("logo.png")
st.sidebar.image(logo, width=250)

# --------------------- File Import ---------------------
st.sidebar.markdown("<h3 style='font-size:18px;'>BHE Setup</h3>", unsafe_allow_html=True)
with st.sidebar.expander("📁 File Import"):
    default_length = 80
    default_load = 50
    df_bhe = None

    tab1, tab2 = st.tabs(["📐 Local Coordinates (meters)", "🧭 GPS Coordinates (EPSG:4326)"])
    with tab1:
        local_file = st.file_uploader("Local Coordinate File (CSV)", type=["csv"], key="local_file")
        if local_file is not None:
            df_raw = pd.read_csv(local_file)
    with tab2:
        gps_file = st.file_uploader("GPS Coordinate File (CSV)", type=["csv"], key="gps_file")
        if gps_file is not None:
            df_raw = pd.read_csv(gps_file)
            transformer = Transformer.from_crs("epsg:4326", "epsg:3857", always_xy=True)  # WGS84 → meters

    # Run shared parsing if any file is loaded
    if 'df_raw' in locals():
        try:
            df_raw.columns = [col.strip().lower() for col in df_raw.columns]

            def detect_column(name_keywords):
                for col in df_raw.columns:
                    if any(keyword in col for keyword in name_keywords):
                        return col
                return None

            lat_col = detect_column(["lat"])
            lon_col = detect_column(["long"])
            len_col = detect_column(["leng"])
            load_col = detect_column(["load"])
            x_col = detect_column(["x"]) if not lon_col else None
            y_col = detect_column(["y"]) if not lat_col else None

            # Resolve coordinates
            if lat_col and lon_col:
                lat_data = df_raw[lat_col]
                lon_data = df_raw[lon_col]
                x_data, y_data = transformer.transform(lon_data.values, lat_data.values)  # GPS → meters
            elif x_col and y_col:
                x_data = df_raw[x_col]
                y_data = df_raw[y_col]
            else:
                st.error("❌ Could not detect coordinate columns (latitude/longitude or x/y).")
                st.stop()

            n_rows = len(x_data)

            h_data = df_raw[len_col] if len_col else np.full(n_rows, st.number_input("Default BHE Length", min_value=10, value=default_length, step=10))
            ql_data = df_raw[load_col] if load_col else np.full(n_rows, st.number_input("Default Heat Load", min_value=0, value=default_load, step=10))

            if all(len(arr) == n_rows for arr in [x_data, y_data, h_data, ql_data]):
                df_bhe = pd.DataFrame({
                    'x': x_data,
                    'y': y_data,
                    'H': h_data,
                    'q_l': ql_data
                })
                bhe_coord = df_bhe[['x', 'y']].values
                bhe_length = df_bhe['H'].values
                bhe_load = df_bhe['q_l'].values
            else:
                st.error("❌ Column lengths do not match. Please check your file.")
                st.stop()
        except Exception as e:
            st.error(f"❌ Error reading or processing CSV: {e}")
            st.stop()
    else:
        st.warning("⚠️ Please upload a file in one of the tabs to continue.")
        st.stop()

# --------------------- BHE Layout Plot ---------------------
st.markdown("<h3 style='font-size:24px; margin-top: 10px; font-weight:600;'>BHE Layout Map</h3>", unsafe_allow_html=True)
with st.expander("🗺️ BHE Map View (Click to expand)", expanded=True):
    if df_bhe is not None:
        is_gps = gps_file is not None  # We assume GPS tab triggers lat/lon, else local
        if is_gps:
            # Plot with Folium (OpenStreetMap)
            lat_center = df_raw[lat_col].mean()
            lon_center = df_raw[lon_col].mean()

            m = folium.Map(location=[lat_center, lon_center+0.001], zoom_start=16, min_zoom=5)
            for i, row in df_raw.iterrows():
                popup_text = (f"<b>BHE {i+1}</b><br>")
                folium.CircleMarker(
                    location=[row[lat_col], row[lon_col]],
                    radius=4,
                    color=None,
                    fill=True,
                    fill_color='red',
                    fill_opacity=0.8,
                    popup=folium.Popup(popup_text, max_width=250)
                ).add_to(m)
            st_folium(m, width=1000, height=500)
        else:
            # Interactive Plotly scatter plot
            fig = px.scatter(
                df_bhe,
                x="x",
                y="y",
                text=[f"{i+1}" for i in df_bhe.index],
                labels={"x": "X (m)", "y": "Y (m)"},
                width=1000,
                height=500
            )
            fig.update_traces(
                marker=dict(size=10, color='red'),
                textposition="top right",
                textfont=dict(family="verdana",size=12,color="black")
            )
            fig.update_layout(
                yaxis=dict(scaleanchor="x", scaleratio=1, titlefont=dict(color="black"),tickfont=dict(color="black")),
                xaxis=dict(showgrid=True, titlefont=dict(color="black"), tickfont=dict(color="black")),  # vertical gridlines
                plot_bgcolor="lightgrey",   # background inside plot
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)
        # Show some basic stats
        from scipy.spatial.distance import pdist
        coords = df_bhe[['x', 'y']].values
        num_bhe = len(df_bhe)
        min_dist = np.min(pdist(coords)) if num_bhe > 1 else None

        st.markdown(f"- **Number of BHEs:** {num_bhe}")
        if min_dist is not None:
            st.markdown(f"- **Minimum distance between BHEs:** {min_dist:.2f} m")
        else:
            st.markdown("- Not enough BHEs to compute distances.")
    else:
        st.warning("⚠️ No layout data to display. Please upload a file above.")

st.sidebar.markdown("<h3 style='font-size:18px;'>Ground Properties</h3>", unsafe_allow_html=True)
with st.sidebar.expander("🌡️ Hydro-thermal Parameters"):
    lamda = st.number_input("Thermal Conductivity (W/m·K)", min_value=0.5, value=2.5) # variable for the following code
    rho_c = st.number_input("Volumetric Heat Capacity (MJ/m^3/K)", value=2.5) # variable for the following code
    u_gw = st.number_input("GW Seepage Velocity (m/s)", value=1e-7, format="%.0001e") # variable for the following code
    theta_gw = st.number_input("GW Flow Direction (°)", value=30) # variable for the following code
    
st.sidebar.markdown("<h3 style='font-size:18px;'>Optimization</h3>", unsafe_allow_html=True)
with st.sidebar.expander("🎯 Goals and Constraints"):
    goal = st.checkbox("Max Net Seasonal Heat Extraction", value=True)
    bhe_temp_min = st.number_input("Lower Bound", value=5) # variable for the following code
    bhe_temp_max = st.number_input("Upper Bound", value=50) # variable for the following code
    max_env_impact = st.number_input("Max Impact to Environment (°C)", value=6.0, step=0.1) # variable for the following code
    max_neighbor_impact = st.number_input("Max Impact from Neighbors (°C)", value=1.5, step=0.1) # variable for the following code
    max_iterations = st.slider("Max Iterations", 10, 200, 50, step=10) # variable for the following code
    ftol = st.number_input("Function Tolerance (ftol)", value=0.1, format="%.0001e") # variable for the following code
    eps = st.number_input("Step Size Tolerance (eps)", value=0.1, format="%.0001e") # variable for the following code

st.sidebar.markdown("<h3 style='font-size:18px;'>Visualization</h3>", unsafe_allow_html=True)
with st.sidebar.expander("🖼️ Plot Options"):
    mesh_density = st.number_input("Grid Density (points)", min_value=1, value=2, step=1) # variable for the following code
    section_depth = st.number_input("Section Depth (m)", min_value=10, value=30, step=10) # variable for the following code

def get_user_params():
    V_T = u_gw * 4.2 / rho_c
    ANGLE = (theta_gw / 180 + 1) * np.pi
    A = lamda / rho_c / 1e6 ##unit: m^2/s

    return {
        "V_T": V_T,
        "ANGLE": ANGLE,
        "A": A,
        "LAMDA": lamda,
        "R_w": 0.1,
        "maxiter": max_iterations,
        "ftol": ftol,
        "eps": eps,
        "lim_env": max_env_impact,
        "lim_neigh": max_neighbor_impact,
        "low_lim": bhe_temp_min,
        "up_lim": bhe_temp_max,
        "point_density": mesh_density,
        "obs_z": section_depth
    }

st.sidebar.markdown("<h3 style='font-size:18px;'>Action</h3>", unsafe_allow_html=True)
col_a1, col_a2, col_a3 = st.sidebar.columns(3)
with col_a1:
    if st.button("🔄 Init ∆T", key="init_dt_btn"):
        st.session_state.show_initial_plot = True

with col_a2:
    if st.button("🚀 Run Opt"):
        params = get_user_params()
        result, logs = run_optimization(
            bhe_coord, bhe_length,
            V_T=params["V_T"], ANGLE=params["ANGLE"],
            A=params["A"], LAMDA=params["LAMDA"],
            point_density=params["point_density"],
            maxiter=params["maxiter"],
            ftol=params["ftol"],
            eps=params["eps"],
            lim_env=params["lim_env"],
            lim_neigh=params["lim_neigh"],
            low_lim=params["low_lim"],
            up_lim=params["up_lim"]
        )
        if result.success:
            st.session_state.optimized_q = result.x
            st.session_state.optimization_logs = logs
            st.success("✅ Optimization completed!")
        else:
            st.error("❌ Optimization failed. Please adjust your parameters.")

with col_a3:
    if st.button("📈 Opt ∆T") and st.session_state.optimized_q is not None:
        st.session_state.show_opt_plot = True

if st.sidebar.button("❌ Clear Plots"):
    st.session_state["show_initial_plot"] = False
    st.session_state["show_opt_plot"] = False
    st.session_state.optimized_q = None

# # --------------------- Main: Visualization ---------------------
st.markdown("<h3 style='font-size:24px; margin-top: 10px; font-weight:600;'>Temperature Change Map under Initial Load</h3>", unsafe_allow_html=True)
with st.expander("🌡️ Ground Temperature Distribution (Click to expand)", expanded=False):
    if st.session_state.get("show_initial_plot", False):
        params = get_user_params()
        summary_ini = plot_initial_heatmap(
            bhe_coord, bhe_length, bhe_load,
            obs_z=params["obs_z"],
            V_T=params["V_T"], ANGLE=params["ANGLE"],
            A=params["A"], LAMDA=params["LAMDA"],
            R_w=params["R_w"], point_density=params["point_density"],
            lim_env=params["lim_env"],lim_neigh=params["lim_neigh"]
        )

        st.markdown(f"""
        - **Min Heat Load**: {summary_ini['min_q']:.1f} W/m and **Max Heat Load**: {summary_ini['max_q']:.1f} W/m  
        - **Max ΔT<sub>g</sub> (ground)**: {summary_ini['max_Tg']:.2f} °C and **Max ΔT<sub>n</sub> (from neighbors)**: {summary_ini['max_Tn']:.2f} °C  
        """, unsafe_allow_html=True)
    else:
        st.info("Click **🔄 Init ΔT** in the sidebar to generate the plot.")


# --- Section: Optimization Logs ---
st.markdown("<h3 style='font-size:24px; margin-top: 10px; font-weight:600;'>Optimization Iteration Log</h3>", unsafe_allow_html=True)
with st.expander("📋 Optimization Progress (Click to expand)", expanded=False):
    logs = st.session_state.get("optimization_logs", [])
    if logs:
        for line in logs:
            st.text(line)
    else:
        st.info("No optimization logs available yet.")

# --- Optimized ΔT Heatmap ---
st.markdown("<h3 style='font-size:24px; margin-top: 10px; font-weight:600;'>Optimized Temperature Change Map</h3>", unsafe_allow_html=True)
with st.expander("🌡️ Ground Temperature After Optimization", expanded=False):
    if st.session_state.get("show_opt_plot", False):
        optimized_q = st.session_state.optimized_q
        params = get_user_params()
        summary_opt = plot_optimized_heatmap(
            sources=bhe_coord,
            optimized_q_l=optimized_q,
            H_array=bhe_length,
            obs_z=params["obs_z"],
            V_T=params["V_T"], ANGLE=params["ANGLE"],
            A=params["A"], LAMDA=params["LAMDA"],
            R_w=params["R_w"], point_density=params["point_density"],
            lim_env=params["lim_env"],lim_neigh=params["lim_neigh"],
        )

        st.markdown(f"""
        - **Min Heat Load**: {summary_opt['min_q']:.1f} W/m and **Max Heat Load**: {summary_opt['max_q']:.1f} W/m  
        - **Max ΔT<sub>g</sub> (ground)**: {summary_opt['max_Tg']:.2f} °C and **Max ΔT<sub>n</sub> (from neighbors)**: {summary_opt['max_Tn']:.2f} °C  
        """, unsafe_allow_html=True)
    else:
        st.info("Click **📈 Opt ΔT** in the sidebar to generate the plot.")

# --- Final Comparison Summary ---
st.markdown("<h3 style='font-size:24px; margin-top: 10px; font-weight:600;'>🔍 Summary: Optimization Comparison</h3>", unsafe_allow_html=True)

if st.session_state.get("show_initial_plot", False) and st.session_state.get("show_opt_plot", False):
    # Use already-computed summaries if they exist
    initial = summary_ini
    optimized = summary_opt

    def check_constraint(value, limit, label, inverse=False):
        condition = value <= limit if not inverse else value >= limit
        symbol = "✅" if condition else "❌"
        return f"{symbol} {label}: {value:.2f} (Limit: {limit})"

    # Heat load totals
    total_initial_q = np.sum(bhe_load)
    total_optimized_q = np.sum(st.session_state.optimized_q)

    st.markdown("**Constraint Check Summary**:")
    st.markdown(f"""
    - {check_constraint(initial['max_Tg'], max_env_impact, 'Initial Max ΔTg')}
    - {check_constraint(initial['max_Tn'], max_neighbor_impact, 'Initial Max ΔTn')}
    - {check_constraint(optimized['max_Tg'], max_env_impact, 'Optimized Max ΔTg')}
    - {check_constraint(optimized['max_Tn'], max_neighbor_impact, 'Optimized Max ΔTn')}
    """)

    st.markdown("**Heat Load Summary:**")
    st.markdown(f"""
    - 🔸 Initial Total Heat Load: **{total_initial_q:.1f} W**
    - 🔹 Optimized Total Heat Load: **{total_optimized_q:.1f} W**
    - 🔁 Change: **{(total_optimized_q - total_initial_q):+.1f} W**
    """)
else:
    st.info("Run both ΔT plots to see comparison summary.")
