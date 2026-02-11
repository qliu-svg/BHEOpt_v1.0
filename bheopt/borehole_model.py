# -*- coding: utf-8 -*-
"""
Created on Tue Mar 25 09:27:20 2025

@author: Siam
"""

# # borehole_model.py
import numpy as np
from scipy.integrate import quad

# z_values can be a vector for computing the T change at multiple depths

def precompute_integrals(z_values, H_array, R_w=0.1):
    z_values = np.asarray(z_values, dtype=float)
    H_array = np.asarray(H_array, dtype=float)

    integrals = []
    for h in H_array:
        source_integrals = {}
        for z in z_values:
            direct = np.arcsinh(z / R_w) - np.arcsinh((z - h) / R_w)
            mirror = np.arcsinh((z + h) / R_w) - np.arcsinh(z / R_w)
            source_integrals[float(z)] = {"direct": float(direct), "mirror": float(mirror)}
        integrals.append(source_integrals)

    return integrals  # list of dicts, one per source

def compute_self_Tchange(z_values, q_l, integrals_for_source, LAMDA):
    z_values = np.asarray(z_values, dtype=float)
    return np.array([
        (q_l / (4 * np.pi * LAMDA)) *
        (integrals_for_source[float(z)]["direct"] - integrals_for_source[float(z)]["mirror"])
        for z in z_values
    ], dtype=float)

def compute_neighbor_Tchange(x, y, z_values, sources, H_array, heat_rates, V_T, ANGLE, A, LAMDA):
    z_values = np.asarray(z_values, dtype=float)

    # Handle empty sources
    if sources is None or len(sources) == 0:
        return np.zeros_like(z_values, dtype=float)

    sources = np.asarray(sources, dtype=float)
    heat_rates = np.asarray(heat_rates, dtype=float)
    H_array = np.asarray(H_array, dtype=float)

    dx = x - sources[:, 0]         # shape: (n_sources,)
    dy = y - sources[:, 1]
    r_sq = dx**2 + dy**2           # shape: (n_sources,)
    vx, vy = V_T * np.cos(ANGLE), V_T * np.sin(ANGLE)
    exp_fac = np.exp(np.clip(-(vx * dx + vy * dy) / (2 * A), -1000, 1000))  # shape: (n_sources,)

    max_h = np.max(H_array)
    z0_grid = np.arange(0, max_h + 1)  # longest possible z0, with a interval of 1m
    z0_mask = z0_grid[None, :] <= (H_array[:, None] + 1e-12)

    z_diff = z_values[None, :, None] - z0_grid[None, None, :]              # (n_sources, n_z, n_z0)
    z_diff_m = z_values[None, :, None] + z0_grid[None, None, :]

    # Regularize distance to prevent r=0
    r = np.sqrt(r_sq[:, None, None] + z_diff**2)
    r_mirror = np.sqrt(r_sq[:, None, None] + z_diff_m**2)

    kernel = np.exp(-V_T * r / (2 * A)) / r
    kernel_m = np.exp(-V_T * r_mirror / (2 * A)) / r_mirror
    # Zero out invalid z0 indices per source using mask
    kernel *= z0_mask[:, None, :]
    kernel_m *= z0_mask[:, None, :]

    # Integrate over z0 (axis=2)
    int_direct = np.trapz(kernel, z0_grid, axis=2)
    int_mirror = np.trapz(kernel_m, z0_grid, axis=2)

    # Compute temperature change
    t = (heat_rates[:, None] / (4 * np.pi * LAMDA)) * exp_fac[:, None] * (int_direct - int_mirror)
    return np.sum(t, axis=0)  # (n_z,)

def compute_temperature_grid(grid_x, grid_y, sources, H_array, heat_rates, obs_z, V_T, ANGLE, A, LAMDA, integrals, node_map):
    temp_map = np.zeros_like(grid_x, dtype=float)
    rows, cols = grid_x.shape

    sources = np.asarray(sources, dtype=float)
    H_array = np.asarray(H_array, dtype=float)
    heat_rates = np.asarray(heat_rates, dtype=float)
    nsrc = len(sources)

    for i in range(rows):
        for j in range(cols):
            x = float(grid_x[i, j])
            y = float(grid_y[i, j])
            key = (i, j)  # node index

            if key in node_map:
                self_idx_list = node_map[key]

                # neighbors = all except those snapped to this node
                mask = np.ones(nsrc, dtype=bool)
                mask[self_idx_list] = False

                t_neigh = compute_neighbor_Tchange(x, y, [obs_z], sources[mask], H_array[mask], heat_rates[mask], V_T=V_T, ANGLE=ANGLE, A=A, LAMDA=LAMDA)[0]

                # sum self terms for all sources snapped to this node
                t_self = 0.0
                for sidx in self_idx_list:
                    t_self += compute_self_Tchange([obs_z], heat_rates[sidx], integrals[sidx], LAMDA)[0]

                temp_map[i, j] = t_self + t_neigh
            else:
                temp_map[i, j] = compute_neighbor_Tchange(x, y, [obs_z], sources, H_array, heat_rates, V_T=V_T, ANGLE=ANGLE, A=A, LAMDA=LAMDA)[0]

    return temp_map