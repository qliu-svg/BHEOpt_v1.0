# -*- coding: utf-8 -*-
"""
Created on Tue Mar 25 09:27:20 2025

@author: Siam
"""

# # borehole_model.py
import numpy as np
from scipy.integrate import quad

# z_values can be a vector for computing the T change at multiple depths

def precompute_integrals(z_values, H_array, R_w):
    integrals = []
    for h in H_array:
        source_integrals = {
            z: {
                "direct": quad(lambda z0: 1 / np.sqrt(R_w**2 + (z - z0)**2), 0, h)[0],
                "mirror": quad(lambda z0: 1 / np.sqrt(R_w**2 + (z - z0)**2), -h, 0)[0]
            } for z in z_values
        }
        integrals.append(source_integrals)
    return integrals  # list of dicts indexed by source

def compute_self_Tchange(z_values, q_l, integrals_for_source, LAMDA):
    return np.array([
        (q_l / (4 * np.pi * LAMDA)) * 
        (integrals_for_source[z]["direct"] - integrals_for_source[z]["mirror"])
        for z in z_values
    ])

def compute_neighbor_Tchange(x, y, z_values, sources, H_array, heat_rates, V_T, ANGLE, A, LAMDA):
    z_values = np.asarray(z_values)

    dx = x - sources[:, 0]         # shape: (n_sources,)
    dy = y - sources[:, 1]
    r_sq = dx**2 + dy**2           # shape: (n_sources,)
    vx, vy = V_T * np.cos(ANGLE), V_T * np.sin(ANGLE)
    exp_fac = np.exp(np.clip(-(vx * dx + vy * dy) / (2 * A), -1000, 1000))  # shape: (n_sources,)

    max_h = np.max(H_array)
    z0_grid = np.arange(0, max_h + 1)  # longest possible z0, with a interval of 1m
    n_z0 = len(z0_grid)
    z0_mask = np.arange(n_z0)[None, :] < (H_array[:, None] + 1)  # shape: (n_sources, n_z0)
    z_diff = z_values[None, :, None] - z0_grid[None, None, :]
    z_diff_m = z_values[None, :, None] + z0_grid[None, None, :]

    # r_sq[:, None, None] → broadcasted to (n_sources, n_z, n_z0)
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
    # print(heat_rates.shape)
    # print(exp_fac.shape)
    # Compute temperature change
    t = (heat_rates[:, None] / (4 * np.pi * LAMDA)) * exp_fac[:, None] * (int_direct - int_mirror)  # shape: (n_sources, n_z)
    return np.sum(t, axis=0)  # shape: (n_z,)


# obs_z represents a specific depth here
def compute_temperature_grid(grid_x, grid_y, sources, H_array, heat_rates, obs_z, V_T, ANGLE, A, LAMDA, integrals, cell_map, x_edges, y_edges):
    temp_map = np.zeros_like(grid_x)
    rows, cols = grid_x.shape

    for i in range(rows):
        for j in range(cols):
            x, y = grid_x[i, j], grid_y[i, j]
            cell_key = (i, j)

            if cell_key in cell_map:
                src_idx = cell_map[cell_key]
                others = np.delete(np.arange(len(sources)), src_idx)
                t_neigh = compute_neighbor_Tchange(x, y, [obs_z], sources[others], H_array[others], heat_rates[others], V_T=V_T, ANGLE=ANGLE, A=A, LAMDA=LAMDA)[0]
                t_self = compute_self_Tchange([obs_z], heat_rates[src_idx], integrals[src_idx], LAMDA)[0]
                temp_map[i, j] = t_self + t_neigh
            else:
                temp_map[i, j] = compute_neighbor_Tchange(x, y, [obs_z], sources, H_array, heat_rates, V_T=V_T, ANGLE=ANGLE, A=A, LAMDA=LAMDA)[0]

    return temp_map

