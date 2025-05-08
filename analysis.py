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
    """Generate analysis plots from the data"""
    # Create figure with subplots
    fig = plt.figure(figsize=(15, 10))
    gs = fig.add_gridspec(2, 2)
    
    # 1. Parameter Distribution
    ax1 = fig.add_subplot(gs[0, 0])
    if data['parameters']:
        params = np.array(data['parameters'])
        ax1.boxplot(params, labels=['SiC3 Porosity', 'SiC10 Porosity', 'Preheating Length'])
        ax1.set_title('Parameter Distributions')
        ax1.set_ylabel('Value')
        ax1.grid(True)
    
    # 2. Fitness vs Parameters
    ax2 = fig.add_subplot(gs[0, 1])
    if data['parameters'] and data['fitness']:
        params = np.array(data['parameters'])
        fitness = np.array(data['fitness'])
        for i, label in enumerate(['SiC3 Porosity', 'SiC10 Porosity', 'Preheating Length']):
            ax2.scatter(params[:, i], fitness, alpha=0.5, label=label)
        ax2.set_title('Heat Release vs Parameters')
        ax2.set_xlabel('Parameter Value')
        ax2.set_ylabel('Heat Release (J)')
        ax2.legend()
        ax2.grid(True)
    
    # 3. Heat vs NOx Trade-off
    ax3 = fig.add_subplot(gs[1, 0])
    if data['fitness'] and data['nox']:
        heat = np.array(data['fitness'])
        nox = np.array([n[0] for n in data['nox']])  # Extract single NOx value
        ax3.scatter(heat, nox, alpha=0.5)
        ax3.set_title('Heat Release vs NOx Emissions')
        ax3.set_xlabel('Heat Release (J)')
        ax3.set_ylabel('NOx Concentration')
        ax3.grid(True)
    
    # 4. Flame Location Distribution
    ax4 = fig.add_subplot(gs[1, 1])
    if data['flame_loc']:
        flame_locs = data['flame_loc']
        ax4.hist(flame_locs, bins=20, alpha=0.7)
        ax4.set_title('Flame Location Distribution')
        ax4.set_xlabel('Location (m)')
        ax4.set_ylabel('Frequency')
        ax4.grid(True)
    
    plt.tight_layout()
    plt.savefig('analysis_results.png')
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
        
        # Generate and save statistics
        stats = generate_summary_statistics(data)
        with open('analysis_statistics.json', 'w') as f:
            json.dump(stats, f, indent=4)
        
        print("\nAnalysis complete! Check:")
        print("- analysis_results.png for visualizations")
        print("- analysis_statistics.json for numerical statistics")
        
    except Exception as e:
        print(f"\nError during analysis: {str(e)}")
        print("Please check that your results file contains valid data in the expected format.")

if __name__ == "__main__":
    main()