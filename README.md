# Burner Optimization Project

## Overview
This project uses a genetic algorithm (GA) to optimize the design of a porous matrix burner. The optimization targets:
- **Porosity of SiC-3PPI section (ε₁)**
- **Porosity of SiC-10PPI section (ε₂)**
- **Preheating length (L_pre)**: the distance from the burner inlet to the flame base

The objective is to maximize heat release from combustion while penalizing NOₓ emissions, using Cantera for physical simulation and DEAP for the GA.

## Problem Formulation
- **Burner geometry:**
  - 2-inch YZA-40PPI preheat zone (inert)
  - 1-inch SiC-3PPI section
  - 1-inch SiC-10PPI section
- **Design variables:**
  - ε₁, ε₂ ∈ [0.75, 0.85] (porosity bounds)
  - L_pre ∈ [0.02, 0.04] m (preheating length bounds)
- **Fitness function:**
  - `fitness = heat_release - w_NOx * NOx_emission - penalty`
    - `heat_release`: total heat released (integral of volumetric heat release)
    - `NOx_emission`: sum of NO and NO₂ at the outlet
    - `penalty`: applied if the flame base (max dT/dx) is not within [0.02, 0.04] m
    - `w_NOx`: penalty weight (tunable)

## What is Preheating Length?
The **preheating length** is the distance from the burner inlet to the base of the flame. It is determined by finding the location of the maximum temperature gradient (or maximum heat release rate) in the simulated temperature profile. This region is where the reactants are heated before ignition occurs.

## Workflow
1. **Genetic Algorithm Setup:**
   - Uses DEAP to define individuals as `[ε₁, ε₂, L_pre]` within the specified bounds.
   - Registers genetic operators (crossover, mutation, selection).
2. **Simulation:**
   - For each individual, a Cantera 1D flame simulation is run with the specified parameters.
   - Extracts heat release, NOx emissions, and flame base location.
3. **Fitness Evaluation:**
   - Computes the fitness as described above.
   - Applies a penalty if the flame base is outside the allowed preheating length.
4. **GA Loop:**
   - Runs for a specified number of generations, evolving the population toward optimal burner parameters.
5. **Results:**
   - The best solution and fitness are saved to `ga_burner_results.txt`.

## Using the Dataset
- The provided `Dataset.xlsx` contains experimental or simulation profiles (position, temperature, species fraction) and can be used to validate the Cantera model or train surrogate models.
- The GA, however, relies on physics-based Cantera simulations for each candidate design.

## How to Run
1. **Install dependencies:**
   - Python 3.8+
   - Required libraries:
     - cantera
     - numpy
     - deap
     - (and their dependencies)
   - Install with:
     ```bash
     pip install cantera numpy deap
     ```
2. **Run the optimization:**
   ```bash
   python solver.py
   ```
   - The script will print progress and save the best result to `ga_burner_results.txt`.

## Future Plan of Action
- **Parameter Tuning:** Adjust the NOx penalty weight (`w_NOx`) to reflect your desired trade-off between heat and emissions.
- **Model Refinement:** Incorporate more detailed porosity effects (e.g., via Cantera’s transport/energy loss models) as needed.
- **Validation:** Compare simulation results with your dataset for model validation.
- **Surrogate Modeling:** Optionally, train a regression or ML model on the dataset to speed up optimization.
- **Parallelization:** The script uses multiprocessing for faster evaluation; you can increase the population size or generations for more thorough search.

## References
- [Cantera 1D Flame Documentation](https://cantera.org/3.1/python/onedim.html)
- [DEAP Genetic Algorithm Library](https://deap.readthedocs.io/en/master/)
- [Material property data for SiC foams](https://pmc.ncbi.nlm.nih.gov/articles/PMC10461437/)