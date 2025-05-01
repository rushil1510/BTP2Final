import numpy as np
import pandas as pd
from scipy.optimize import curve_fit, minimize
from deap import base, creator, tools, algorithms
import random

# Load dataset
DATASET_PATH = "Dataset.xlsx"
data = pd.read_excel(DATASET_PATH)

# Extract z (position), Temperature, and Concentration
z = data['z'].values
T = data['Temperature'].values
concentration = data['Concentration'].values

# Fit NOx equation to find C1 and C2
def nox_model(T, C1, C2):
    return C1 * np.exp(C2 * T)

params, _ = curve_fit(nox_model, T, concentration)
C1, C2 = params

# Calculate heating value (example: integral approximation)
def calculate_heating_value(T):
    return np.trapz(T, z)  # Approximate integral of T over z

# Fitness function: F = T - a * NOx
def fitness_function(individual, a):
    porosity_sic3, porosity_sic10, preheating_length = individual

    # Simulate burner (placeholder for actual simulation logic)
    simulated_T = np.mean(T) + random.uniform(-50, 50)  # Mock temperature
    simulated_NOx = nox_model(simulated_T, C1, C2)      # Calculate NOx

    # Fitness value
    return simulated_T - a * simulated_NOx,

# Genetic Algorithm setup
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

# Toolbox setup
toolbox = base.Toolbox()
toolbox.register("attr_float", random.uniform, 0.7, 0.9)  # Porosity range
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_float, n=3)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

toolbox.register("mate", tools.cxBlend, alpha=0.5)
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=0.05, indpb=0.2)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("evaluate", fitness_function, a=1)  # Default a=1

# Run Genetic Algorithm
def run_genetic_algorithm(a_values):
    results = []
    for a in a_values:
        toolbox.unregister("evaluate")
        toolbox.register("evaluate", fitness_function, a=a)

        pop = toolbox.population(n=50)
        hof = tools.HallOfFame(1)

        algorithms.eaSimple(pop, toolbox, cxpb=0.7, mutpb=0.2, ngen=100, stats=None, halloffame=hof, verbose=False)

        best_individual = hof[0]
        results.append((best_individual[0], best_individual[1], best_individual[2]))

    return results

# Gradient Descent Optimization
def gradient_descent_optimization(a_values):
    def objective_function(individual, a):
        porosity_sic3, porosity_sic10, preheating_length = individual

        # Simulate burner (placeholder for actual simulation logic)
        simulated_T = np.mean(T) + random.uniform(-50, 50)  # Mock temperature
        simulated_NOx = nox_model(simulated_T, C1, C2)      # Calculate NOx

        # Objective value (negative fitness for minimization)
        return -(simulated_T - a * simulated_NOx)

    results = []
    for a in a_values:
        res = minimize(objective_function, x0=[0.8, 0.8, 0.8], args=(a,), bounds=[(0.7, 0.9), (0.7, 0.9), (0.7, 0.9)])
        results.append(tuple(res.x))

    return results

if __name__ == "__main__":
    a_values = [1, 100, 1000, 10000, 100000, 1000000]

    # Run Genetic Algorithm
    ga_results = run_genetic_algorithm(a_values)

    # Run Gradient Descent
    gd_results = gradient_descent_optimization(a_values)

    # Save results to file
    with open("results.txt", "w") as f:
        f.write("Genetic Algorithm Results:\n")
        for result in ga_results:
            f.write(f"{result}\n")

        f.write("\nGradient Descent Results:\n")
        for result in gd_results:
            f.write(f"{result}\n")