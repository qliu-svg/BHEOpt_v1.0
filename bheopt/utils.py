"""
Created on Wed Feb 11 10:21:54 2026

@author: qliu
"""

# utils.py
import numpy as np
from scipy.spatial.distance import cdist

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
    x_range = (x_min - 0.1 * x_span, x_max + 0.1 * x_span)
    y_range = (y_min - 0.1 * y_span, y_max + 0.1 * y_span)

    x_grid = np.arange(x_range[0], x_range[1] + spacing, spacing)
    y_grid = np.arange(y_range[0], y_range[1] + spacing, spacing)
    xx, yy = np.meshgrid(x_grid, y_grid)
    return xx, yy, x_grid, y_grid

def assign_sources_to_nearest_nodes(sources, x_grid, y_grid):
    sources = np.asarray(sources, dtype=float)
    xg = np.asarray(x_grid, dtype=float)
    yg = np.asarray(y_grid, dtype=float)

    # Assumes uniform spacing grid_x/grid_y from arange
    dx = float(xg[1] - xg[0]) if len(xg) > 1 else 1.0
    dy = float(yg[1] - yg[0]) if len(yg) > 1 else 1.0

    node_map = {}
    for idx, (x, y) in enumerate(sources):
        j = int(np.rint((x - xg[0]) / dx))
        i = int(np.rint((y - yg[0]) / dy))
        j = int(np.clip(j, 0, len(xg) - 1))
        i = int(np.clip(i, 0, len(yg) - 1))
        node_map.setdefault((i, j), []).append(idx)

    return node_map
