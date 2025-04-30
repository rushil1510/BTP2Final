import numpy as np
from genetic_algorithm import GeneticAlgorithm
from optimization import GradientDescentOptimizer
from data_processing import load_dataset, fit_nox_equation
import json
import pandas as pd

def run_optimizations(alpha_values, dataset_path):
    """Run both GA and GD optimizations for different alpha values and sheets"""
    # Get all sheet names
    xl = pd.ExcelFile(dataset_path)
    sheet_names = xl.sheet_names
    
    results = {}
    
    for sheet_name in sheet_names:
        print(f"\nProcessing sheet: {sheet_name}")
        results[sheet_name] = {}
        
        # Load and process dataset
        positions, temperatures, concentrations = load_dataset(dataset_path, sheet_name)
        C1, C2 = fit_nox_equation(temperatures, concentrations)
        
        print(f"Fitted NOx parameters: C1={C1:.4f}, C2={C2:.4f}")
        
        for alpha in alpha_values:
            print(f"\nRunning optimizations for alpha = {alpha}")
            
            # Genetic Algorithm
            ga = GeneticAlgorithm(population_size=50, generations=100)
            ga_params, ga_fitness = ga.optimize(alpha, C1, C2)
            
            # Gradient Descent
            gd = GradientDescentOptimizer(learning_rate=0.01, max_iterations=1000)
            gd_params, gd_fitness = gd.optimize(alpha, C1, C2)
            
            results[sheet_name][alpha] = {
                'genetic_algorithm': {
                    'parameters': ga_params.tolist(),
                    'fitness': float(ga_fitness)
                },
                'gradient_descent': {
                    'parameters': gd_params.tolist(),
                    'fitness': float(gd_fitness)
                }
            }
            
            print(f"\nResults for alpha = {alpha}:")
            print(f"GA: Parameters = {ga_params}, Fitness = {ga_fitness}")
            print(f"GD: Parameters = {gd_params}, Fitness = {gd_fitness}")
        
        # Save results after each sheet
        with open('results.json', 'w') as f:
            json.dump(results, f, indent=4)

if __name__ == "__main__":
    alpha_values = [1, 100, 1000, 10000, 100000, 1000000]
    dataset_path = "Dataset.xlsx"
    
    run_optimizations(alpha_values, dataset_path) 