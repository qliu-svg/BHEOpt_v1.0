# BHEOpt V1.0

**BHEOpt** is an open-source software tool (with a web-based GUI) for long-term temperature-disturbance
simulation and constrained thermal-load optimization of clustered borehole heat exchanger (BHE) fields
under site-specific hydrothermal conditions, including advective heat transport associated with
groundwater flow.

The software supports:
- **Forward simulation** of temperature change fields using moving finite line source (MFLS)
  formulations and superposition principle on a structured grid.
- **Thermal-load optimization** under nonlinear constraints on environmental temperature change and 
  thermal interference between BHEs.

> Paper: *BHEOpt V1.0: Open-source software with a GUI for borehole heat exchanger field simulation and thermal load optimization considering groundwater flow*  
> Target journal: *Computers & Geosciences*  
> License: MIT

---

## Features

- Import borehole layouts from CSV (geographic or local coordinates)
- Long-term temperature-disturbance simulation including groundwater advection (MFLS)
- Structured-grid evaluation and spatial diagnostics (2D horizontal slices)
- Constrained thermal-load optimization (SLSQP) with user-defined thresholds:
  - environmental temperature change limit: \(\Delta T_{\mathrm{env}}\)
  - neighbor-induced thermal interference limit: \(\Delta T_{\mathrm{nb}}\)
- Performance options for large arrays (e.g., parallel evaluation of source–target interactions)

---

## Installation

### Option A: Install from source (recommended)

```bash
git clone https://github.com/<ORG>/<REPO>.git
cd <REPO>
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate  # Windows
pip install -U pip
pip install -r requirements.txt
```

**Tested on:** [Windows], Python [3.11].

---

## Quickstart (GUI)

Run the Streamlit application:

```bash
streamlit run app.py
```

Then in the GUI:
1. Upload a borehole CSV (see `examples/inputs/`).
2. Enter hydrothermal parameters (\(\lambda\), \(\rho c\), groundwater velocity and direction).
3. Set thresholds (\(\Delta T_{\mathrm{env}}\), \(\Delta T_{\mathrm{nb}}\)) and solver settings.
4. Run simulation and/or optimization and inspect outputs.

---

## Input format

### Borehole CSV

A minimal CSV should contain (column names can be configured in the GUI):

| column | description | unit |
|---|---|---|
| id | borehole identifier | – |
| x, y | coordinates (local) **OR** lon, lat (geographic) | m or degrees |
| H | borehole length | m |
| q0 | initial thermal load per length | W/m |

Example: `examples/inputs/boreholes_example.csv`

### Key parameters


λ: ground thermal conductivity [W/m/K]

ρc: volumetric heat capacity [J/m³/K]

u_w: Darcy seepage velocity [m/s]

θ: groundwater flow direction [deg]

Δx, Δy, Δz: grid spacing [m]

r_cutoff: influence-radius cutoff [m] (optional)




---

## Reproducibility

Scripts and example inputs are provided to reproduce key results from the paper:

- Forward-model validation case:
  - Inputs: `examples/inputs/validation_case/`
  - Command: `python scripts/run_forward_validation.py`
- Optimization validation case:
  - Inputs: `examples/inputs/optimization_case/`
  - Command: `python scripts/run_optimization_validation.py`
- Case study (Göttingen):
  - Inputs: `examples/inputs/goettingen_case/`
  - Command: `python scripts/run_case_study.py`

Outputs (figures/tables) are written to:
- `outputs/figures/`
- `outputs/tables/`
- `outputs/logs/`

> Note: COMSOL models are not included. The repository reproduces BHEOpt results; COMSOL is used in the manuscript


---

## Performance notes (large BHE fields)

Runtime is sensitive to grid resolution and the number of source–target interactions. BHEOpt provides options to reduce
compute time:

- **Parallel evaluation** of superposition terms (multi-threading via joblib)
- **Influence-radius cutoff** to ignore distant source contributions (e.g., \(r > r_{\mathrm{cutoff}}\))
- **Moderate vertical coarsening** for planning-stage runs

---

## Project structure

```text
<REPO>/
  app.py                      # Streamlit entry point
  bheopt/                      # core library
    io/                        # input parsing, validation
    forward/                   # FLS/MFLS models + superposition
    optimize/                  # objective + constraints + SLSQP
    viz/                       # plotting utilities
  examples/                    # example inputs and configs
  scripts/                     # reproducibility scripts
  requirements.txt
  LICENSE
```

---



## License

This project is released under the **MIT License** (see `LICENSE`).

---

## Contact

For questions or issues, please open a GitHub issue or contact:
- Dr. Quan Liu, quan.liu@geo.uni-goettingen.de
