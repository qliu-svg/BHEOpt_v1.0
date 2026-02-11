"""
Created on Wed Feb 11 10:21:54 2026

@author: qliu
"""

import pandas as pd
import matplotlib.pyplot as plt

# 1) Load your CSV
df = pd.read_csv("BHE_generated_200.csv")

# 2) Plot points
plt.figure(figsize=(5, 4.7))
plt.scatter(df["x"], df["y"], s=30, alpha=0.9)  # s=marker size

# 3) Make it look nice
plt.xlabel("X (m)", fontsize=22)
plt.ylabel("Y (m)", fontsize=22)
plt.xticks(fontsize=18)
plt.yticks(fontsize=18)
# plt.title("Locations (x, y)")
plt.xlim(-50, 550)
plt.ylim(-50, 550)
# plt.axis("equal")
plt.grid(True, linewidth=0.5, alpha=0.4)
plt.tight_layout()
plt.show()
# plt.savefig("test1.png", bbox_inches="tight", dpi=300)


