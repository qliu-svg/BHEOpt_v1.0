# -*- coding: utf-8 -*-
"""
Created on Sat Apr 12 08:42:42 2025

@author: Siam
"""

import numpy as np
import plotly.graph_objects as go

# Load both .npz files
temp1 = np.load('temp_interp_opt_BHEOpt_gm_30m.npy')
# temp2 = np.load('temp_interp_opt_BHEOpt_gm_60m.npy')
temp2 = np.load('temp_interp_opt_comsol_gm_30m.npy')

# Compute absolute difference
temp_diff = np.abs(temp1 - temp2)

# --- Remove source locations from temp_diff by setting them to NaN ---
source_points = [(-25, -15), (-25, -5), (-15, -15), (-15, -5), (-5, -15),
                 (5, 5), (5, 15), (15, 5), (25, 5)]

x1d = np.linspace(-50, 50, 1001)
y1d = np.linspace(-50, 50, 1001)

dx = x1d[1] - x1d[0]
dy = y1d[1] - y1d[0]
x_min = x1d[0]
y_min = y1d[0]

radius_m = 0.2
r = int(np.ceil(radius_m / dx))

for xs, ys in source_points:
    j0 = int(round((xs - x_min) / dx))
    i0 = int(round((ys - y_min) / dy))
    i1, i2 = max(0, i0 - r), min(temp_diff.shape[0], i0 + r + 1)
    j1, j2 = max(0, j0 - r), min(temp_diff.shape[1], j0 + r + 1)
    temp_diff[i1:i2, j1:j2] = np.nan



# Define the grid
x = np.linspace(-50, 50, 1001)
y = np.linspace(-50, 50, 1001)
x, y = np.meshgrid(x, y)

# Plot the absolute temperature difference
fig = go.Figure(data=go.Contour(
    z=temp_diff,
    x=x[0],
    y=y[:, 0],
    colorscale='Viridis_r',  # or 'Plasma', 'Viridis', 'RdBu', etc.
    contours=dict(
        labelfont=dict(family="Verdana", size=18, color='white'),
        showlines=False,
        start=0,
        end=0.2,
        size=0.02,
        coloring='fill'
    ),
    colorbar=dict(
        title="|ΔT| (°C)",
        titlefont=dict(size=34, family="Verdana", color='black'),
        tickfont=dict(size=30, family="Verdana", color='black'),
        len=0.75
    )
))

# Update layout to lock aspect ratio
fig.update_layout(
    xaxis=dict(
        title="X (m)",
        showgrid=False,
        zeroline=False,
        scaleanchor="y",
        titlefont=dict(size=38, family="Verdana", color='black'),
        tickfont=dict(size=34, family="Verdana", color='black')
    ),
    yaxis=dict(
        title="Y (m)",
        showgrid=False,
        zeroline=False,
        scaleanchor="x",
        scaleratio=1,
        titlefont=dict(size=38, family="Verdana", color='black'),
        tickfont=dict(size=34, family="Verdana", color='black')
    ),
    width=875,   # pixels
    height=740,   # pixels
)

# ---- Find and mark maximum temp_diff (ignoring NaNs) ----
imax = np.nanargmax(temp_diff)
i_max, j_max = np.unravel_index(imax, temp_diff.shape)

x_max = x1d[j_max]
y_max = y1d[i_max]
v_max = temp_diff[i_max, j_max]

# Add a marker + label for the maximum
fig.add_trace(go.Scatter(
    x=[x_max],
    y=[y_max],
    mode="markers+text",
    text=[f"{v_max:.2f}"],
    textposition="top right",
    textfont=dict(size=28, family="Verdana", color='black'),
    marker=dict(size=15, symbol="x", color="black"),
    showlegend=False
))

# Show the plot in browser
fig.show(renderer="browser")