# -*- coding: utf-8 -*-
"""
Created on Tue Mar 25 09:27:58 2025

@author: Siam
"""

# optimization.py
import numpy as np
from scipy.optimize import minimize
from joblib import Parallel, delayed
from borehole_model import compute_self_Tchange, compute_neighbor_Tchange, precompute_integrals

def compute_max_BHE_Tchange(i, locations, heat_rates, z_values, integrals, H_array, V_T, ANGLE, A, LAMDA):
    x, y = locations[i]
    mask = np.arange(len(locations)) != i
    sources = locations[mask]
    neighbor_rates = heat_rates[mask]
    self_rate = heat_rates[i]

    dx = np.abs(sources[:, 0] - x)
    dy = np.abs(sources[:, 1] - y)
    close = (dx <= 500) & (dy <= 500)
    sources = sources[close]
    neighbor_rates = neighbor_rates[close]

    t_neigh = compute_neighbor_Tchange(x, y, z_values, sources, H_array[mask], neighbor_rates, V_T=V_T, ANGLE=ANGLE, A=A, LAMDA=LAMDA,)
    t_self = compute_self_Tchange(z_values, self_rate, integrals[i], LAMDA)
    return np.max(t_neigh), np.max(t_neigh + t_self.T)

def optimize_heat_load(locations, H_array, callback_logger, V_T, ANGLE, A, LAMDA, R_w, maxiter, ftol, eps, lim_env, lim_neigh, low_lim, up_lim, initial_q=None, obs_z_range=(10, 70), obs_z_step=10):
    n = len(locations)
    initial_q = np.full(n, 10.0) if initial_q is None else initial_q
    bounds = [(low_lim, up_lim)] * n
    z_values = list(range(obs_z_range[0], obs_z_range[1] + obs_z_step, obs_z_step))
    integrals = precompute_integrals(z_values, H_array, R_w)
    constraint_cache = {}

    def round_key(q): return tuple(np.round(q, 3))

    def evaluate_constraints(q):
        key = round_key(q)
        if key in constraint_cache:
            return constraint_cache[key]

        results = Parallel(n_jobs=-1)(
            delayed(compute_max_BHE_Tchange)(i, locations, q, z_values, integrals, H_array, V_T, ANGLE, A, LAMDA)
            for i in range(n))
        
        results = np.array(results)
        max_neigh = np.max(results[:, 0])
        max_env = np.max(results[:, 1])
        constraint_cache[key] = (max_env, max_neigh)
        return max_env, max_neigh

    def constraint_env(q): return lim_env - evaluate_constraints(q)[0]
    def constraint_neigh(q): return lim_neigh - evaluate_constraints(q)[1]

    def objective(q): return -np.sum(q)

    iteration = {'count': 0}

    def callback(q):
        iteration['count'] += 1
        max_env, max_neigh = evaluate_constraints(q)
        msg = f"📊 Iter {iteration['count']:>2}: Load={np.sum(q):.2f}, MaxΔT_env={max_env:.2f}, MaxΔT_neigh={max_neigh:.2f}"
        print(msg)
        if callback_logger:
            callback_logger(msg)
    
    result = minimize(
        fun=objective,
        x0=initial_q,
        bounds=bounds,
        method='SLSQP',
        constraints=[
            {'type': 'ineq', 'fun': constraint_env},
            {'type': 'ineq', 'fun': constraint_neigh}
        ],
        callback=callback,
        options={'disp': True, 'maxiter': maxiter, 'ftol': ftol, 'eps': eps}
    )
    
    q_opt = result.x
    max_env, max_neigh = evaluate_constraints(q_opt)

    result.max_env = max_env
    result.max_neigh = max_neigh
    result.res_env = 6.0 - max_env        # >=0 means satisfied
    result.res_neigh = 1.5 - max_neigh    # >=0 means satisfied

    return result
