import numpy as np
from data_processing import calculate_fitness, calculate_nox_emissions

class GradientDescentOptimizer:
    def __init__(self, learning_rate=0.01, max_iterations=1000):
        self.learning_rate = learning_rate
        self.max_iterations = max_iterations
        
        # Parameter bounds
        self.sic3_bounds = (0.1, 0.9)
        self.sic10_bounds = (0.1, 0.9)
        self.length_bounds = (0.1, 1.0)
    
    def clip_params(self, params):
        """Ensure parameters stay within bounds"""
        params[0] = np.clip(params[0], *self.sic3_bounds)
        params[1] = np.clip(params[1], *self.sic10_bounds)
        params[2] = np.clip(params[2], *self.length_bounds)
        return params
    
    def compute_gradient(self, params, alpha, C1, C2, h=1e-6):
        """Compute numerical gradient"""
        gradient = np.zeros_like(params)
        for i in range(len(params)):
            params_plus = params.copy()
            params_minus = params.copy()
            params_plus[i] += h
            params_minus[i] -= h
            
            # Compute function values
            f_plus = self.objective_function(params_plus, alpha, C1, C2)
            f_minus = self.objective_function(params_minus, alpha, C1, C2)
            
            gradient[i] = (f_plus - f_minus) / (2 * h)
        return gradient
    
    def objective_function(self, params, alpha, C1, C2):
        """Compute objective function value"""
        temperature = self.simulate_burner(params)
        nox = calculate_nox_emissions(temperature, C1, C2)
        return calculate_fitness(temperature, nox, alpha)
    
    def simulate_burner(self, params):
        """Simulate burner with given parameters"""
        # Same simulation as in genetic algorithm
        sic3_porosity, sic10_porosity, length = params
        return 1000 + 500 * sic3_porosity + 300 * sic10_porosity + 200 * length
    
    def optimize(self, alpha, C1, C2):
        """Run gradient descent optimization"""
        # Initialize parameters randomly within bounds
        params = np.array([
            np.random.uniform(*self.sic3_bounds),
            np.random.uniform(*self.sic10_bounds),
            np.random.uniform(*self.length_bounds)
        ])
        
        best_params = params.copy()
        best_value = float('-inf')
        
        for iteration in range(self.max_iterations):
            # Compute gradient
            gradient = self.compute_gradient(params, alpha, C1, C2)
            
            # Update parameters
            params = params + self.learning_rate * gradient
            params = self.clip_params(params)
            
            # Compute objective value
            current_value = self.objective_function(params, alpha, C1, C2)
            
            # Track best solution
            if current_value > best_value:
                best_value = current_value
                best_params = params.copy()
            
            if iteration % 100 == 0:
                print(f"Iteration {iteration}, Best Value: {best_value}")
        
        return best_params, best_value 