# Burner Parameter Optimization

This project implements genetic algorithms and gradient descent to optimize burner parameters for maximizing heating value while minimizing NOx emissions.

## Project Structure

- `data_processing.py`: Handles dataset loading and processing, NOx equation fitting, and fitness calculations
- `genetic_algorithm.py`: Implements the genetic algorithm optimization
- `optimization.py`: Implements gradient descent optimization
- `main.py`: Main script that runs both optimizations and saves results
- `results.json`: Output file containing optimization results

## Dependencies

- Python 3.7+
- numpy
- pandas
- scipy
- openpyxl (for Excel file handling)

Install dependencies using:
```bash
pip install numpy pandas scipy openpyxl
```

## Usage

1. Place your dataset in an Excel file named `Dataset.xlsx` with columns:
   - position
   - temperature
   - concentration

2. Run the optimization:
```bash
python main.py
```

## Optimization Parameters

The code optimizes three parameters:
1. SiC3 porosity (range: 0.1-0.9)
2. SiC10 porosity (range: 0.1-0.9)
3. Preheating length (range: 0.1-1.0)

## Fitness Function

The fitness function used is:
```
F = T - α*NOx
```
where:
- T is the temperature
- NOx is calculated using C1*exp(C2*T)
- α is a weighting factor (tested values: 1, 100, 1000, 10000, 100000, 1000000)

## Alternative Fitness Functions

1. Multiplicative form:
```
F = T / (1 + α*NOx)
```

2. Exponential form:
```
F = exp(T) - α*NOx
```

3. Weighted sum with normalization:
```
F = w1*(T/T_max) - w2*(NOx/NOx_max)
```

## Results

Results are saved in `results.json` with the following structure:
```json
{
    "alpha_value": {
        "genetic_algorithm": {
            "parameters": [sic3_porosity, sic10_porosity, length],
            "fitness": fitness_value
        },
        "gradient_descent": {
            "parameters": [sic3_porosity, sic10_porosity, length],
            "fitness": fitness_value
        }
    }
}
```

## Comparison of Methods

The genetic algorithm and gradient descent approaches are compared based on:
1. Convergence speed
2. Solution quality
3. Robustness to different α values
4. Computational efficiency

## Notes

- The burner simulation is currently a simplified model. For real-world applications, it should be replaced with a proper physics-based simulation.
- The NOx equation parameters (C1, C2) are fitted from the provided dataset.
- Both optimization methods use the same parameter bounds and fitness function for fair comparison.
