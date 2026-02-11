# -*- coding: utf-8 -*-
"""
Created on Wed Jan 28 19:13:27 2026

@author: siam
"""

import random
import math
import csv

# -------- settings --------
N = 200
WIDTH = 500.0     # domain size in x [m]
HEIGHT = 500.0    # domain size in y [m]
MIN_DIST = 20.0   # minimum spacing [m]
H = 80.0          # borehole length [m]
Q0 = 10.0         # thermal load [W/m]
SEED = 42
OUT_CSV = "BHE_generated_200.csv"
MAX_TRIES = 1_000_000
# -------------------------

random.seed(SEED)
min_dist2 = MIN_DIST * MIN_DIST

points = []
tries = 0

while len(points) < N and tries < MAX_TRIES:
    tries += 1
    x = random.uniform(0, WIDTH)
    y = random.uniform(0, HEIGHT)

    ok = True
    for (px, py) in points:
        if (x - px) ** 2 + (y - py) ** 2 < min_dist2:
            ok = False
            break

    if ok:
        points.append((x, y))

if len(points) < N:
    raise RuntimeError("Failed to place points. Increase WIDTH/HEIGHT or lower N/MIN_DIST.")

with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["id", "x", "y", "H", "q0"])
    for i, (x, y) in enumerate(points, start=1):
        w.writerow([i, round(x, 3), round(y, 3), H, Q0])

print(f"Saved {N} boreholes to {OUT_CSV}")
