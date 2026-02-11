# BHEOpt V1.0

**BHEOpt** is an open-source software tool (with a web-based GUI) for long-term temperature disturbance
simulation and constrained thermal-load optimization of clustered borehole heat exchanger (BHE) fields
under site-specific hydrothermal conditions, including advective heat transport induced by
groundwater flow.

The software supports:
- **Forward simulation** of temperature change fields using moving finite line source (MFLS)
  formulations and superposition principle on a structured grid.
- **Thermal-load optimization** under nonlinear constraints on environmental temperature change and 
  thermal interference between BHEs.

> Paper: *BHEOpt V1.0: Open-source software with a GUI for borehole heat exchanger field simulation and thermal load optimization with groundwater flow effects*  
> Target journal: *Computers & Geosciences*  
> License: MIT

---

## Features

- Import borehole layouts from CSV (geographic or local coordinates, with BHE length and initial loads)
- Long-term temperature-disturbance simulation including groundwater advection
- Structured-grid evaluation and spatial diagnostics (2D horizontal slices)
- Constrained thermal-load optimization (SLSQP) with user-defined thresholds:
  - environmental temperature change limit: ΔT_env
  - neighbor-induced thermal interference limit: ΔT_nb
- Performance options for large arrays (e.g., parallel evaluation of source–target interactions)

---

## Installation

**Prerequisites**
- Install **Miniconda** or **Anaconda**

```bash
git clone https://github.com/qliu-svg/BHEOpt_v1.0.git
cd BHEOpt_v1.0-main
conda env create -f environment.yml
conda activate bheopt
streamlit run bheopt/GUI.py
```

**Tested on:** [Windows], Python [3.11].

---

## Quickstart (GUI)

Run the Streamlit application:

```bash
streamlit run bheopt/GUI.py
```

Then in the GUI:
1. Upload a borehole CSV (see `examples/`).
2. Enter hydrothermal parameters (λ, ρc, groundwater velocity and direction).
3. Set thresholds (ΔT_env, ΔT_nb) and solver settings.
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

Example: `examples/BHE_***.csv`

### Key parameters

- λ: ground thermal conductivity [W/m/K]
- ρc: volumetric heat capacity [MJ/m³/K]
- u_w: Darcy seepage velocity [m/s]
- θ: groundwater flow direction [deg]
- Δx, Δy: grid spacing [m]
- r_virtual: influence-radius cutoff [m]

---

## Reproducibility

Scripts and example inputs are provided to reproduce key results from the paper:

- Forward-model and optimization validation case:
  - Inputs: `examples/validation_case/`

- Sensitivity case:
  - Inputs: `examples/sensitivity_case/`

- Case study:
  - Inputs: `examples/application/`

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

  bheopt/                      # core library
    GUI.py                     # Streamlit entry point
    borehole_model/            # FLS/MFLS models + superposition + temperature change field simulation
    main_refactor/             # plotting for temperature change field under initial and optimized loads + optimization operation
    optimization/              # analytically computating of defined constraints + solving the objective issue
    utils/                     # numerical utilities
    visualization/             # plotting utilities
  examples/                    # example inputs and configs
  environment.yml
  LICENSE
```

---



## License

This project is released under the **MIT License** (see `LICENSE`).

---

## Contact

For questions or issues, please open a GitHub issue or contact:
- Dr. Quan Liu, quan.liu@geo.uni-goettingen.de
