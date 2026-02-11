# -*- coding: utf-8 -*-
"""
Created on Sat Mar 29 08:17:58 2025

@author: Siam
"""

# main_refactor.py
import streamlit as st
from utils import find_closest_pair, create_extended_grid, assign_sources_to_nearest_nodes
from borehole_model import precompute_integrals
from visualization import plot_temperature_heatmap
from optimization import optimize_heat_load

def plot_initial_heatmap(sources, H_array, heat_rates, obs_z, V_T, ANGLE, A, LAMDA, R_w, point_density, lim_env, lim_neigh):
    (_, _), min_dist = find_closest_pair(sources)
    grid_spacing = min_dist / point_density
    grid_x, grid_y, x_grid, y_grid = create_extended_grid(sources, grid_spacing)
    source_cell_map = assign_sources_to_nearest_nodes(sources, x_grid, y_grid)
    integrals = precompute_integrals([obs_z], H_array, R_w=grid_spacing)
    summary = plot_temperature_heatmap(
        grid_x, grid_y,
        sources=sources,
        H_array=H_array,
        heat_rates=heat_rates,
        obs_z=obs_z, V_T=V_T, ANGLE=ANGLE, A=A, LAMDA=LAMDA, 
        integrals=integrals,
        node_map=source_cell_map,
        lim_env=lim_env, lim_neigh=lim_neigh,
        title_suffix="(Initial Load)"
    )

    summary["min_q"] = float(min(heat_rates))
    summary["max_q"] = float(max(heat_rates))
    return summary

def plot_optimized_heatmap(sources, optimized_q_l, H_array, obs_z, V_T, ANGLE, A, LAMDA, R_w, point_density, lim_env, lim_neigh):
    (_, _), min_dist = find_closest_pair(sources)
    spacing = min_dist / point_density
    grid_x, grid_y, x_grid, y_grid = create_extended_grid(sources, spacing)
    cell_map = assign_sources_to_nearest_nodes(sources, x_grid, y_grid)
    integrals = precompute_integrals([obs_z], H_array, R_w=spacing)
    summary = plot_temperature_heatmap(
        grid_x, grid_y,
        sources=sources,
        H_array=H_array,
        heat_rates=optimized_q_l,
        obs_z=obs_z, V_T=V_T, ANGLE=ANGLE, A=A, LAMDA=LAMDA, 
        integrals=integrals,
        node_map=cell_map,
        lim_env=lim_env, lim_neigh=lim_neigh,
        title_suffix="(After Optimization)"
    )

    summary["min_q"] = float(min(optimized_q_l))
    summary["max_q"] = float(max(optimized_q_l))
    return summary

def run_optimization(sources, H_array, V_T, ANGLE, A, LAMDA, point_density, maxiter, ftol, eps, lim_env, lim_neigh, low_lim, up_lim):
    logs = []
    (_, _), min_dist = find_closest_pair(sources)
    spacing = min_dist / point_density

    def logger(msg):
        logs.append(msg)
    result = optimize_heat_load(sources, H_array, callback_logger=logger, V_T=V_T, ANGLE=ANGLE, A=A, LAMDA=LAMDA, R_w=spacing, maxiter=maxiter, ftol=ftol, eps=eps, lim_env=lim_env, lim_neigh=lim_neigh, low_lim=low_lim, up_lim=up_lim)
    return result, logs
