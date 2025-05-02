import cantera as ct
import numpy as np
from deap import base, creator, tools, algorithms
import random
import multiprocessing

# --- GA parameter bounds ---
POROSITY_MIN, POROSITY_MAX = 0.75, 0.85
L_PRE_MIN, L_PRE_MAX = 0.02, 0.04  # meters

# --- Fitness penalty weight for NOx ---
w_NOx = 1e5  # Adjust as needed for your system

# --- Burner geometry (meters) ---
YZA_LENGTH = 0.0508  # 2 inches
SIC3_LENGTH = 0.0254  # 1 inch
SIC10_LENGTH = 0.0254  # 1 inch

# --- Cantera setup ---
FUEL = 'CH4'
PHI = 0.6
P = ct.one_atm
TIN = 300.0  # K

# --- Fitness evaluation function ---
def evaluate(individual):
    eps1, eps2, Lpre = individual
    try:
        # Set up gas object
        gas = ct.Solution('gri30.yaml')
        gas.set_equivalence_ratio(PHI, FUEL, 'O2:0.21,N2:0.79')
        gas.TP = TIN, P

        # Domain: preheat (YZA), SiC3, SiC10
        width = Lpre + SIC3_LENGTH + SIC10_LENGTH
        flame = ct.FreeFlame(gas, width=width)
        flame.set_refine_criteria(ratio=3, slope=0.06, curve=0.12)
        flame.transport_model = 'Mix'
        flame.inlet.T = TIN
        flame.inlet.X = gas.X
        flame.P = P

        # Optionally, adjust transport/heat loss to mimic porosity (advanced)
        # For now, just note the porosity values in the individual
        # (You can extend this to modify transport/energy loss as needed)

        # Solve flame
        flame.solve(loglevel=0, auto=True, refine_grid=True)

        # Extract heat release (integral over domain)
        heat_release = np.trapz(flame.heat_release_rate, flame.grid)

        # Extract NOx (sum of NO and NO2 at outlet)
        no = flame.Y[gas.species_index('NO'), :]
        no2 = flame.Y[gas.species_index('NO2'), :]
        NOx = np.max(no + no2)  # or use outlet value: (no + no2)[-1]

        # Find flame base (max dT/dx)
        dTdx = np.gradient(flame.T, flame.grid)
        flame_index = np.argmax(dTdx)
        flame_location = flame.grid[flame_index]

        # Penalty if flame base not within Lpre bounds
        penalty = 0.0
        if not (L_PRE_MIN <= flame_location <= L_PRE_MAX):
            penalty += 1e6 * abs(flame_location - np.clip(flame_location, L_PRE_MIN, L_PRE_MAX))

        # Fitness: maximize heat, penalize NOx and flame location
        fitness = heat_release - w_NOx * NOx - penalty
        return (fitness,)
    except Exception as e:
        # If Cantera fails, return a very poor fitness
        return (-1e12,)

# --- DEAP GA setup ---
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("attr_por1", random.uniform, POROSITY_MIN, POROSITY_MAX)
toolbox.register("attr_por2", random.uniform, POROSITY_MIN, POROSITY_MAX)
toolbox.register("attr_len", random.uniform, L_PRE_MIN, L_PRE_MAX)
toolbox.register("individual", tools.initCycle, creator.Individual,
                 (toolbox.attr_por1, toolbox.attr_por2, toolbox.attr_len), n=1)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("mate", tools.cxBlend, alpha=0.5)
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=0.01, indpb=0.2)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("evaluate", evaluate)

def main():
    pop_size = 20
    ngen = 10
    cxpb = 0.7
    mutpb = 0.2

    pop = toolbox.population(n=pop_size)
    hof = tools.HallOfFame(1)

    # Parallel evaluation
    pool = multiprocessing.Pool()
    toolbox.register("map", pool.map)

    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("std", np.std)
    stats.register("min", np.min)
    stats.register("max", np.max)

    pop, log = algorithms.eaSimple(pop, toolbox, cxpb=cxpb, mutpb=mutpb,
                                   ngen=ngen, stats=stats, halloffame=hof, verbose=True)
    pool.close()
    pool.join()

    print("Best individual:", hof[0])
    print("Best fitness:", hof[0].fitness.values[0])
    # Save results
    with open("ga_burner_results.txt", "w") as f:
        f.write(f"Best individual: {hof[0]}\n")
        f.write(f"Best fitness: {hof[0].fitness.values[0]}\n")
        f.write(str(log))

if __name__ == "__main__":
    main()
