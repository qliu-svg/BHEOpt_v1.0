"""
Created on Wed Feb 11 10:21:54 2026

@author: qliu
"""

# visualization.py
import numpy as np
import streamlit as st
from borehole_model import compute_neighbor_Tchange, compute_temperature_grid, compute_self_Tchange
import plotly.graph_objects as go

def plot_temperature_heatmap(grid_x, grid_y, sources, H_array, heat_rates, obs_z, V_T, ANGLE, A, LAMDA, integrals, node_map, lim_env, lim_neigh, title_suffix=""):
    # Compute temperature grid
    temp_map = compute_temperature_grid(
        grid_x, grid_y,
        sources=sources,
        H_array=H_array,
        heat_rates=heat_rates,
        obs_z=obs_z, V_T=V_T, ANGLE=ANGLE, A=A, LAMDA=LAMDA, 
        integrals=integrals,
        node_map=node_map,
    )
    
    fig = go.Figure()
    max_Tg = 0  # Track maximum ground impact
    max_Tn = 0  # Track maximum neighbor impact

    # Add contour heatmap
    fig.add_trace(go.Contour(
        z=temp_map,
        x=grid_x[0],        # 1D X array
        y=grid_y[:, 0],     # 1D Y array
        contours=dict(
            coloring='fill',
            showlabels=True,
            labelfont=dict(family="Verdana", size=12, color='white'),
            showlines=False,
            start=0,
            end=lim_env,
            size=0.5,
        ),
        line=dict(color='white'),
        colorscale='Turbo',
        zmin=0,
        zmax=lim_env,
        colorbar=dict(
            title="ΔT<sub>g</sub> (°C)",
            titlefont=dict(size=14, family="Verdana", color='black'),
            tickfont=dict(size=12, family="Verdana", color='black'),
            tickvals=np.arange(0, lim_env, 1),
            len=0.75
        ),
        hovertemplate="x: %{x}<br>y: %{y}<br>ΔT<sub>g</sub>: %{z:.2f}°C<extra></extra>"
    ))

    # Add BHE markers with two distinct categories
    legend_added = {"circle": False, "x": False}
    min_heat = np.min(heat_rates)
    max_heat = np.max(heat_rates)

    for i, (x, y) in enumerate(sources):
        other_ids = np.delete(np.arange(len(sources)), i)
        t_neigh = compute_neighbor_Tchange(
            x, y, [obs_z],
            sources[other_ids],
            H_array[other_ids],
            heat_rates[other_ids], V_T=V_T, ANGLE=ANGLE, A=A, LAMDA=LAMDA,
        )[0]
        t_self = compute_self_Tchange([obs_z], heat_rates[i], integrals[i], LAMDA)
        # print(t_self.T)
        t_total = t_neigh + t_self.T
        
        max_Tg = max(max_Tg, t_total)
        max_Tn = max(max_Tn, t_neigh)

        # Marker scaling
        if max_heat != min_heat:
            marker_size = 8 + (heat_rates[i] - min_heat) / (max_heat - min_heat) * (16 - 8)
        else:
            marker_size = 12  # default size
        
        threshold_Tn = lim_neigh
        if t_neigh > threshold_Tn+ 0.1:
            symbol = "x"
            label = f"ΔT<sub>n</sub> > {threshold_Tn}°C"
            marker_style = dict(
                size=marker_size,
                symbol=symbol,
                color='black'
            )
        else:
            symbol = "circle"
            label = f"ΔT<sub>n</sub> ≤ {threshold_Tn}°C"
            marker_style = dict(
                size=marker_size,
                symbol=symbol,
                color='white',
                line=dict(color='black', width=1)
            )

        showlegend = not legend_added[symbol]
        legend_added[symbol] = True

        fig.add_trace(go.Scatter(
            x=[x],
            y=[y],
            mode='markers+text',
            name=label,
            textposition="top right",
            marker=marker_style,
            showlegend=showlegend,
            hovertemplate=(
                f"BHE {i+1}<br>"
                f"ΔT<sub>n</sub>: {t_neigh:.2f}°C<br>"
                f"Heat Load: {heat_rates[i]:.1f} W/m"
                "<extra></extra>"
            )
        ))

    # Layout settings
    fig.update_layout(
        title=f"Heat Map of Temperature Change at z = {obs_z} m {title_suffix}".strip(),
        autosize=False,
        xaxis=dict(
            title="X (m)",
            showgrid=False,
            titlefont=dict(color='black'),
            tickfont=dict(color='black')
        ),
        yaxis=dict(
            title="Y (m)",
            showgrid=False,
            zeroline=False,
            scaleanchor="x",
            scaleratio=1,
            titlefont=dict(color='black'),
            tickfont=dict(color='black')
        ),
        font=dict(color='black'),
        legend=dict(
            title="      BHE Legend",
            title_font=dict(color='black', size=14),
            font=dict(color='black', size=14),
            x=0.8,
            y=0.95,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="gray",
            borderwidth=1
        ),
        hoverlabel=dict(
            font_size=12,
            font_family="Verdana",
            font_color="black",
            bgcolor="white"
        ),
        width=1000,
        height=700,
        margin=dict(l=20, r=20, t=60, b=40)
    )

    # Show the plot
    st.plotly_chart(fig, use_container_width=True)

    # Return key summary values
    return {
        "max_Tg": float(max_Tg),
        "max_Tn": float(max_Tn),
        "min_q": float(min_heat),
        "max_q": float(max_heat)
    }

