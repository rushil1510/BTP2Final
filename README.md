# README for Burner Optimization Project

## Overview
This project uses genetic algorithms and gradient descent to optimize the parameters of a burner described in `PorousMediaBurner.py`. The goal is to maximize the heating value while minimizing NOx emissions.

## Files
1. **genetic_algorithm.py**: Contains the implementation of the genetic algorithm and gradient descent for optimization.
2. **Dataset.xlsx**: The dataset used for temperature and concentration values.
3. **results.txt**: Stores the results of the optimization for both genetic algorithms and gradient descent.
4. **PorousMediaBurner.py**: Placeholder for the burner simulation logic.

## Dependencies
- Python 3.8+
- Required libraries:
  - numpy
  - pandas
  - scipy
  - deap

Install dependencies using:
```bash
pip install numpy pandas scipy deap
```

## Instructions to Run
1. Ensure `Dataset.xlsx` is in the same directory as the code.
2. Run the optimization script:
```bash
python genetic_algorithm.py
```
3. Results will be saved in `results.txt`.

## Explanation of Modules and Functions
### genetic_algorithm.py
- **nox_model**: Fits the NOx equation to the dataset to find constants C1 and C2.
- **calculate_heating_value**: Approximates the heating value using the integral of temperature over position.
- **fitness_function**: Defines the fitness function as `F = T - a * NOx`.
- **run_genetic_algorithm**: Runs the genetic algorithm for a range of `a` values.
- **gradient_descent_optimization**: Performs gradient descent optimization for the same range of `a` values.

### results.txt
- Contains tuples of optimized parameters `(SiC3 porosity, SiC10 porosity, preheating length)` for both methods.

## Alternate Fitness Function Suggestions
1. **Weighted Heating Value**: `F = w1 * T - w2 * NOx`, where `w1` and `w2` are weights.
2. **Logarithmic Penalty**: `F = T - log(1 + NOx)`.
3. **Inverse NOx**: `F = T - 1/(1 + NOx)`.

## Comparison
The results in `results.txt` allow comparison of genetic algorithms and gradient descent in terms of performance and parameter optimization.