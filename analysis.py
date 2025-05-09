# analysis.py
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import json
import yaml
from pathlib import Path

# --- Constants from solver.py ---
L_PRE_MIN, L_PRE_MAX = 0.02, 0.04
POROSITY_MIN, POROSITY_MAX = 0.75, 0.85

def load_results(file_path):
    """Load results from either JSON or YAML file"""
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
        
    if file_path.stat().st_size == 0:
        raise ValueError(f"File is empty: {file_path}")
        
    if file_path.suffix == '.json':
        with open(file_path, 'r') as f:
            data = json.load(f)
    elif file_path.suffix in ['.yml', '.yaml']:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
    if not data:
        raise ValueError(f"No data found in file: {file_path}")
        
    return data

def extract_optimization_data(results):
    """Extract optimization data from results"""
    data = {
        'parameters': [],
        'fitness': [],
        'temperature': [],
        'nox': [],
        'flame_loc': []
    }
    
    # Handle different result formats
    if isinstance(results, dict):
        if 'results' in results and isinstance(results['results'], list):
            # List-based results format
            for result in results['results']:
                try:
                    # Extract parameters (porosities and Lpre)
                    if 'porosities' in result and 'Lpre' in result:
                        params = result['porosities'] + [result['Lpre']]
                        data['parameters'].append(params)
                    
                    # Use Heat as fitness
                    if 'Heat' in result:
                        data['fitness'].append(result['Heat'])
                    
                    # Extract NOx and Flame location
                    if 'NOx' in result:
                        data['nox'].append([result['NOx']])  # Wrap in list for consistency
                    if 'Flame' in result:
                        data['flame_loc'].append(result['Flame'])
                except Exception as e:
                    print(f"Warning: Skipping result due to error: {str(e)}")
                    continue
                
        elif 'parameters' in results:
            # Single result format
            data['parameters'].append(results['parameters'])
            data['fitness'].append(results['fitness'])
            if 'simulation_results' in results:
                sim_results = results['simulation_results']
                data['temperature'].append(sim_results.get('temperature', []))
                data['nox'].append(sim_results.get('nox_concentration', []))
                data['flame_loc'].append(sim_results.get('flame_location', []))
        else:
            # Multiple results format
            for sheet_name, sheet_data in results.items():
                for alpha, methods in sheet_data.items():
                    for method, result in methods.items():
                        data['parameters'].append(result['parameters'])
                        data['fitness'].append(result['fitness'])
                        if 'simulation_results' in result:
                            sim_results = result['simulation_results']
                            data['temperature'].append(sim_results.get('temperature', []))
                            data['nox'].append(sim_results.get('nox_concentration', []))
                            data['flame_loc'].append(sim_results.get('flame_location', []))
    
    # Validate that we have some data
    if not any(len(v) > 0 for v in data.values()):
        raise ValueError("No valid data found in results")
        
    return data

def generate_analysis_plots(data):
    """Generate analysis plots from the data as separate figures."""
    import matplotlib.pyplot as plt
    import numpy as np

    # 1. Parameter Distribution (Boxplot)
    if data['parameters']:
        params = np.array(data['parameters'])
        plt.figure(figsize=(7, 5))
        plt.boxplot(params, labels=['SiC3 Porosity', 'SiC10 Porosity', 'Preheating Length'])
        plt.title('Parameter Distributions')
        plt.ylabel('Value')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig('parameter_distributions.png')
        plt.close()

    # 2. Fitness vs Parameters (Scatter)
    if data['parameters'] and data['fitness']:
        params = np.array(data['parameters'])
        fitness = np.array(data['fitness'])
        for i, label in enumerate(['SiC3 Porosity', 'SiC10 Porosity', 'Preheating Length']):
            plt.figure(figsize=(7, 5))
            plt.scatter(params[:, i], fitness, alpha=0.5)
            plt.title(f'Heat Release vs {label}')
            plt.xlabel(label)
            plt.ylabel('Heat Release (J)')
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(f'heat_vs_{label.lower().replace(" ", "_")}.png')
            plt.close()

    # 3. Heat vs NOx Trade-off (Scatter)
    if data['fitness'] and data['nox']:
        heat = np.array(data['fitness'])
        nox = np.array([n[0] for n in data['nox']])  # Extract single NOx value
        plt.figure(figsize=(7, 5))
        plt.scatter(heat, nox, alpha=0.5)
        plt.title('Heat Release vs NOx Emissions')
        plt.xlabel('Heat Release (J)')
        plt.ylabel('NOx Concentration')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig('heat_vs_nox.png')
        plt.close()

    # 4. Flame Location Distribution (Histogram)
    if data['flame_loc']:
        flame_locs = data['flame_loc']
        plt.figure(figsize=(7, 5))
        plt.hist(flame_locs, bins=20, alpha=0.7)
        plt.title('Flame Location Distribution')
        plt.xlabel('Location (m)')
        plt.ylabel('Frequency')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig('flame_location_distribution.png')
        plt.close()

def generate_additional_plots(data):
    """Generate additional analysis plots for optimization progress and parameter evolution."""
    import matplotlib.pyplot as plt
    import numpy as np

    # 1. Peak Fitness vs Generation (if generations can be inferred)
    if data['fitness']:
        fitness = np.array(data['fitness'])
        # Assume each 20 results = 1 generation (adjust if needed)
        gen_size = 20
        generations = len(fitness) // gen_size
        if generations > 0:
            peak_fitness = [np.max(fitness[i*gen_size:(i+1)*gen_size]) for i in range(generations)]
            plt.figure()
            plt.plot(range(1, generations+1), peak_fitness, marker='o')
            plt.title('Peak Fitness vs Generation')
            plt.xlabel('Generation')
            plt.ylabel('Peak Heat Release (J)')
            plt.grid(True)
            plt.savefig('peak_fitness_vs_generation.png')
            plt.close()

    # 2. Parameter Evolution Across Individuals
    if data['parameters']:
        params = np.array(data['parameters'])
        plt.figure(figsize=(10, 6))
        for i, label in enumerate(['SiC3 Porosity', 'SiC10 Porosity', 'Preheating Length']):
            plt.plot(params[:, i], label=label)
        plt.title('Parameter Evolution Across Individuals')
        plt.xlabel('Individual Index')
        plt.ylabel('Parameter Value')
        plt.legend()
        plt.grid(True)
        plt.savefig('parameter_evolution.png')
        plt.close()

    # 3. Fitness Distribution Histogram
    if data['fitness']:
        plt.figure()
        plt.hist(data['fitness'], bins=30, alpha=0.7)
        plt.title('Fitness (Heat Release) Distribution')
        plt.xlabel('Heat Release (J)')
        plt.ylabel('Frequency')
        plt.grid(True)
        plt.savefig('fitness_distribution.png')
        plt.close()

    # 4. 3D Scatter: Fitness vs SiC3 Porosity vs Preheating Length
    if data['parameters'] and data['fitness']:
        from mpl_toolkits.mplot3d import Axes3D
        params = np.array(data['parameters'])
        fitness = np.array(data['fitness'])
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(params[:, 0], params[:, 2], fitness, c=fitness, cmap='viridis', alpha=0.7)
        ax.set_xlabel('SiC3 Porosity')
        ax.set_ylabel('Preheating Length')
        ax.set_zlabel('Heat Release (J)')
        ax.set_title('Fitness vs SiC3 Porosity vs Preheating Length')
        plt.savefig('fitness_vs_sic3por_lpre.png')
        plt.close()

def generate_summary_statistics(data):
    """Generate summary statistics from the data"""
    stats = {}
    
    if data['parameters']:
        params = np.array(data['parameters'])
        stats['parameters'] = {
            'mean': np.mean(params, axis=0).tolist(),
            'std': np.std(params, axis=0).tolist(),
            'min': np.min(params, axis=0).tolist(),
            'max': np.max(params, axis=0).tolist()
        }
    
    if data['fitness']:
        fitness = np.array(data['fitness'])
        stats['fitness'] = {
            'mean': float(np.mean(fitness)),
            'std': float(np.std(fitness)),
            'min': float(np.min(fitness)),
            'max': float(np.max(fitness))
        }
    
    if data['flame_loc']:
        flame_locs = data['flame_loc']
        stats['flame_location'] = {
            'mean': float(np.mean(flame_locs)),
            'std': float(np.std(flame_locs)),
            'min': float(np.min(flame_locs)),
            'max': float(np.max(flame_locs))
        }
    
    return stats

def main():
    # Try to load results from different possible files
    result_files = ['results.json', 'results.yml', 'results.yaml']
    results = None
    error_messages = []
    
    for file in result_files:
        try:
            results = load_results(file)
            print(f"Successfully loaded results from {file}")
            break
        except FileNotFoundError:
            error_messages.append(f"File not found: {file}")
            continue
        except ValueError as e:
            error_messages.append(f"Error in {file}: {str(e)}")
            continue
        except Exception as e:
            error_messages.append(f"Unexpected error with {file}: {str(e)}")
            continue
    
    if results is None:
        print("\nFailed to load any results file. Errors encountered:")
        for msg in error_messages:
            print(f"- {msg}")
        print("\nPlease ensure you have a valid results file (results.json, results.yml, or results.yaml) with data.")
        return
    
    try:
        # Extract and process data
        data = extract_optimization_data(results)
        
        # Generate plots
        generate_analysis_plots(data)
        generate_additional_plots(data)
        
        # Generate and save statistics
        stats = generate_summary_statistics(data)
        with open('analysis_statistics.json', 'w') as f:
            json.dump(stats, f, indent=4)
        
        print("\nAnalysis complete! Check:")
        print("- analysis_results.png for visualizations")
        print("- analysis_statistics.json for numerical statistics")
        print("- peak_fitness_vs_generation.png for GA progress")
        print("- parameter_evolution.png for parameter trends")
        print("- fitness_distribution.png for fitness histogram")
        print("- fitness_vs_sic3por_lpre.png for 3D parameter-fitness relation")
        
    except Exception as e:
        print(f"\nError during analysis: {str(e)}")
        print("Please check that your results file contains valid data in the expected format.")

if __name__ == "__main__":
    main()