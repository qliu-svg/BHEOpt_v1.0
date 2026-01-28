# -*- coding: utf-8 -*-
"""
Created on Tue Mar 25 09:18:06 2025

@author: Siam
"""

# utils.py
import numpy as np
from scipy.spatial.distance import cdist

# def generate_sources(n_sources, xlim=(0, 500), ylim=(0, 500)):
#     x = np.random.uniform(*xlim, n_sources)
#     y = np.random.uniform(*ylim, n_sources)
#     return np.column_stack((x, y))

# def generate_sources(n_sources, xlim=(0, 1000), ylim=(0, 1000), min_dist=20):
#     sources = []

#     while len(sources) < n_sources:
#         # Generate a batch of random points (e.g., 10 at a time)
#         batch_size = max(10, n_sources - len(sources))
#         new_points = np.random.uniform(
#             low=(xlim[0], ylim[0]), 
#             high=(xlim[1], ylim[1]), 
#             size=(batch_size, 2)
#         )
#         if sources:
#             sources_array = np.array(sources)
#             for point in new_points:
#                 # Compute axis-wise distance to all existing sources
#                 diffs = np.abs(sources_array - point)
#                 if np.all(diffs >= min_dist, axis=1).all():
#                     sources.append(point)
#                     if len(sources) == n_sources:
#                         break
#         else:
#             sources.append(new_points[0])
#     return np.array(sources)
# a = generate_sources(70)

def find_closest_pair(sources):
    dist_matrix = cdist(sources, sources)
    np.fill_diagonal(dist_matrix, np.inf)
    min_idx = np.unravel_index(np.argmin(dist_matrix), dist_matrix.shape)
    min_dist = dist_matrix[min_idx]
    return min_idx, min_dist

def create_extended_grid(sources, spacing):
    x_min, x_max = sources[:, 0].min(), sources[:, 0].max()
    y_min, y_max = sources[:, 1].min(), sources[:, 1].max()
    x_span, y_span = x_max - x_min, y_max - y_min
    x_range = (x_min - 0.25 * x_span, x_max + 0.25 * x_span)
    y_range = (y_min - 0.25 * y_span, y_max + 0.25 * y_span)

    x_grid = np.arange(x_range[0], x_range[1] + spacing, spacing)
    y_grid = np.arange(y_range[0], y_range[1] + spacing, spacing)
    xx, yy = np.meshgrid(x_grid, y_grid)
    return xx, yy, x_grid, y_grid

def assign_sources_to_cells_digitize(sources, x_edges, y_edges):
    source_to_cell = {}
    for idx, (x, y) in enumerate(sources):
        i = np.digitize(x, x_edges) - 1
        j = np.digitize(y, y_edges) - 1
        source_to_cell[(j, i)] = idx
    return source_to_cell
