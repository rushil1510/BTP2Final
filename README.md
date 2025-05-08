# Burner Parameter Optimization with ANSYS Integration

## Overview

This project implements a multi-objective optimization framework for porous matrix burners, focusing on maximizing heating value and minimizing NOx emissions. The optimization leverages genetic algorithms (GA) and gradient descent (GD), with direct integration to ANSYS for CFD simulation and validation. The workflow is designed for research and engineering applications in combustion, energy systems, and burner design.

## Project Structure

- `ansys_interface.py`: Handles all interactions with ANSYS, including geometry creation (APDL), Fluent setup (journal files), parameter management, and simulation execution. Also provides result extraction stubs.
- `Dataset.xlsx`: Experimental or simulation dataset for model fitting and validation.
- `main.tex`: LaTeX report template for documenting methodology, results, and discussion.
- `README.md`: Project documentation and usage guide.
- `requirements.txt`: Python dependencies for running the optimization and data processing scripts.
- `results.yml`/`results.rtf`: Output files containing optimization and simulation results.
- `solver.py`: Main script for running the optimization (GA/GD) and managing the workflow.

## Optimization Workflow

1. **Data Preparation**
   - Load and preprocess the dataset from `Dataset.xlsx`.
   - Fit empirical models for NOx estimation and other performance metrics.

2. **Parameter Configuration**
   - Simulation parameters are managed in `params.txt` (auto-generated/updated by scripts).
   - Key parameters: SiC3 porosity, SiC10 porosity, preheating length, burner geometry, inlet conditions, fuel composition, equivalence ratio.

3. **Optimization**
   - Choose optimization method: Genetic Algorithm (GA) or Gradient Descent (GD).
   - GA uses population-based search, crossover, mutation, and selection to explore the parameter space.
   - GD uses gradient information (if available) for local optimization.
   - Fitness function balances peak temperature and NOx emissions (customizable).

4. **ANSYS Integration**
   - Geometry is created using APDL scripts based on current parameters.
   - Fluent simulation is set up via journal files, including energy/species models and boundary conditions.
   - Simulations are run automatically, and results are extracted for fitness evaluation.

5. **Result Analysis**
   - Results are saved in `results.yml` or `results.json` for further analysis and reporting.
   - The LaTeX report (`main.tex`) can be updated with figures and tables from the results.

## Detailed Module Descriptions

### ansys_interface.py
- **Parameter Management**: Reads/writes `params.txt` for simulation parameters.
- **Geometry Creation**: Generates APDL scripts to define burner geometry and porous regions.
- **Fluent Setup**: Creates journal files for Fluent, configuring models, materials, and boundary conditions.
- **Simulation Execution**: Runs ANSYS Mechanical and Fluent in batch mode using system calls.
- **Result Extraction**: Placeholder for extracting temperature, NOx, and velocity from Fluent output files.

### solver.py
- **Optimization Orchestration**: Runs the selected optimization algorithm, updates parameters, triggers ANSYS simulations, and evaluates fitness.
- **Fitness Function**: Customizable, typically a weighted sum of peak temperature and NOx emissions.
- **Constraint Handling**: Ensures physical and operational constraints are respected during optimization.

### Dataset.xlsx
- Contains experimental or simulated data for model fitting, validation, and empirical NOx estimation.

### main.tex
- LaTeX template for documenting the project, including introduction, methodology, results, and references.

## Parameter Configuration (`params.txt`)

Example:
```
sic3_porosity = 0.5
sic10_porosity = 0.5
preheating_length = 0.5
burner_diameter = 0.1
burner_length = 0.3
inlet_velocity = 0.5
inlet_temperature = 300
fuel_composition = CH4
equivalence_ratio = 0.8
```

Parameters are automatically updated by the optimization scripts.

## Running the Project

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
2. **Prepare Dataset**
   - Ensure `Dataset.xlsx` is present and formatted correctly.
3. **Configure ANSYS**
   - Ensure ANSYS 2023R1+ and Fluent are installed and licensed.
   - Update ANSYS path in `ansys_interface.py` if needed.
4. **Run Optimization**
   ```bash
   python solver.py
   ```
   - The script will run the optimization, update parameters, trigger ANSYS simulations, and save results.

## ANSYS Integration Details

- **Geometry Creation**: APDL scripts define a cylindrical burner with two porous regions (SiC3 and SiC10), with material properties set by porosity.
- **Fluent Setup**: Journal files configure energy/species models, boundary conditions, and run the simulation.
- **Simulation Execution**: Scripts are run in batch mode; results are written to output files for extraction.
- **Result Extraction**: (To be implemented) Parse Fluent output for temperature, NOx, and velocity profiles.

## Optimization Algorithms

- **Genetic Algorithm (GA)**: Population size, generations, mutation rate, and parent selection are configurable. Handles nonlinear, multi-objective optimization.
- **Gradient Descent (GD)**: For problems where gradients are available or can be estimated.
- **Fitness Function**: Default is `Fitness = Tmax - 100 * NOx`, but can be customized for multi-objective or constraint-based optimization.

## Results

- Results are saved in `results.yml` or `results.json` with detailed parameter sets, fitness values, and simulation outputs.
- Example structure:
```json
{
  "parameters": [0.765, 0.836, 0.0376],
  "fitness": 1295.64,
  "simulation_results": {
    "temperature": [...],
    "nox_concentration": [...],
    "velocity": [...]
  }
}
```

## Troubleshooting

- **ANSYS Path Issues**: Update the path in `ansys_interface.py` if ANSYS is not detected.
- **Simulation Convergence**: Adjust mesh density, solution parameters, or boundary conditions in the APDL/Fluent scripts.
- **Optimization Stagnation**: Tune GA parameters (population, mutation rate) or fitness weights.
- **Result Extraction**: Implement or update the extraction logic in `ansys_interface.py` as needed for your Fluent output format.

## References
- See `main.tex` for a full list of academic references and background reading.

## Contact
For questions or contributions, contact Rushil Mital (rushil.mital.es121@dese.iitd.ac.in).