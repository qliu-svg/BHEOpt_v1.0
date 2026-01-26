# BHEOpt V1.0
**BHEOpt** is an open-source software tool (with a web-based GUI) for long-term
temperature disturbance simulation and constrained thermal load optimization of
clustered borehole heat exchanger (BHE) fields under site-specific hydrothermal
conditions, including advective heat transport associated with groundwater flow.

The software supports (i) forward simulation of temperature change fields using
moving finite line source formulations and superposition principle on
a structured grid generated automatically with uder-defined mesh reslution, 
and (ii) nonlinear constrained thermal-load optimization
subject to limits on environmental temperature change and thermal
interference between BHEs.

> Paper: *BHEOpt V1.0: Open-source software with a GUI for borehole heat exchanger field simulation and thermal load optimization considering groundwater flow*  
> Journal submission: *Computers & Geosciences*  
> Repository: https://github.com/<ORG>/<REPO>

---

## Features
- Import borehole layouts from CSV (geographic or local coordinates)
- Long-term temperature-disturbance simulation with groundwater advection (MFLS)
- Structured-grid evaluation and spatial diagnostics (2D horizontal slices)
- Constrained thermal-load optimization (SLSQP) with user-defined thresholds:
  - environmental temperature change limit (ΔT_env)
  - neighbor-induced thermal interference limit (ΔT_nb)
- Performance options for large arrays (e.g., parallel evaluation of source–target interactions)

---

## Installation

```bash
git clone https://github.com/<ORG>/<REPO>.git
cd <REPO>
python -m venv .venv
source .venv\Scripts\activate   # Windows

pip install -U pip
pip install -r requirements.txt

