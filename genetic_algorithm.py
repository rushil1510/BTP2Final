import numpy as np
from data_processing import calculate_fitness, calculate_nox_emissions, calculate_heating_value

class GeneticAlgorithm:
    def __init__(self, population_size=50, generations=100, mutation_rate=0.1):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        
        # Parameter bounds
        self.sic3_bounds = (0.1, 0.9)  # Porosity bounds for SiC3
        self.sic10_bounds = (0.1, 0.9)  # Porosity bounds for SiC10
        self.length_bounds = (0.1, 1.0)  # Preheating length bounds
        
    def initialize_population(self):
        """Initialize random population within bounds"""
        population = np.zeros((self.population_size, 3))
        population[:, 0] = np.random.uniform(*self.sic3_bounds, self.population_size)
        population[:, 1] = np.random.uniform(*self.sic10_bounds, self.population_size)
        population[:, 2] = np.random.uniform(*self.length_bounds, self.population_size)
        return population
    
    def evaluate_fitness(self, population, alpha, C1, C2):
        """Evaluate fitness for each individual in population"""
        fitness = np.zeros(self.population_size)
        for i in range(self.population_size):
            # Simulate burner with current parameters
            # This is a placeholder - actual simulation would be more complex
            temperature = self.simulate_burner(population[i])
            nox = calculate_nox_emissions(temperature, C1, C2)
            fitness[i] = calculate_fitness(temperature, nox, alpha)
        return fitness
    
    def select_parents(self, population, fitness):
        """Select parents using tournament selection"""
        parents = np.zeros((self.population_size, 3))
        for i in range(self.population_size):
            # Tournament selection
            tournament = np.random.choice(self.population_size, 3)
            winner = tournament[np.argmax(fitness[tournament])]
            parents[i] = population[winner]
        return parents
    
    def crossover(self, parents):
        """Perform crossover between parents"""
        children = np.zeros((self.population_size, 3))
        for i in range(0, self.population_size, 2):
            if i + 1 < self.population_size:
                # Single point crossover
                crossover_point = np.random.randint(1, 3)
                children[i] = np.concatenate([parents[i][:crossover_point], 
                                            parents[i+1][crossover_point:]])
                children[i+1] = np.concatenate([parents[i+1][:crossover_point], 
                                              parents[i][crossover_point:]])
        return children
    
    def mutate(self, children):
        """Apply mutation to children"""
        for i in range(self.population_size):
            if np.random.random() < self.mutation_rate:
                # Mutate one parameter
                param_idx = np.random.randint(3)
                if param_idx == 0:
                    children[i, 0] = np.random.uniform(*self.sic3_bounds)
                elif param_idx == 1:
                    children[i, 1] = np.random.uniform(*self.sic10_bounds)
                else:
                    children[i, 2] = np.random.uniform(*self.length_bounds)
        return children
    
    def simulate_burner(self, params):
        """Simulate burner with given parameters"""
        # Placeholder for actual burner simulation
        # This would be replaced with actual physics-based simulation
        sic3_porosity, sic10_porosity, length = params
        # Simple linear relationship for demonstration
        return 1000 + 500 * sic3_porosity + 300 * sic10_porosity + 200 * length
    
    def optimize(self, alpha, C1, C2):
        """Run genetic algorithm optimization"""
        population = self.initialize_population()
        best_fitness = float('-inf')
        best_params = None
        
        for generation in range(self.generations):
            fitness = self.evaluate_fitness(population, alpha, C1, C2)
            parents = self.select_parents(population, fitness)
            children = self.crossover(parents)
            children = self.mutate(children)
            population = children
            
            # Track best solution
            current_best_idx = np.argmax(fitness)
            if fitness[current_best_idx] > best_fitness:
                best_fitness = fitness[current_best_idx]
                best_params = population[current_best_idx]
                
            if generation % 10 == 0:
                print(f"Generation {generation}, Best Fitness: {best_fitness}")
        
        return best_params, best_fitness 