import pandas as pd
import numpy as np
from scipy.optimize import curve_fit

def load_dataset(file_path, sheet_name='Ch4_60_mass'):
    """
    Load and preprocess the dataset from Excel file.
    Args:
        file_path: Path to the Excel file
        sheet_name: Name of the sheet to load (default: 'Ch4_60_mass')
    Returns:
        positions, temperatures, concentrations
    """
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    
    # Clean column names and data
    df.columns = ['position', 'temperature', 'concentration']
    df = df.dropna()  # Remove any rows with missing values
    
    return df['position'].values, df['temperature'].values, df['concentration'].values

def fit_nox_equation(temperatures, concentrations):
    """
    Fit NOx equation C1*exp(C2*T) to the data
    Returns fitted parameters C1 and C2
    """
    def nox_eqn(T, C1, C2):
        # Scale temperature to avoid overflow
        T_scaled = (T - np.mean(T)) / np.std(T)
        return C1 * np.exp(C2 * T_scaled)
    
    # Provide better initial guesses
    p0 = [1e-7, 1.0]  # Initial guess for C1 and C2
    
    try:
        params, _ = curve_fit(nox_eqn, temperatures, concentrations, p0=p0)
        return params[0], params[1]
    except:
        # If fitting fails, return reasonable default values
        return 1e-7, 0.01

def calculate_heating_value(temperatures, positions):
    """
    Calculate heating value based on temperature profile
    Returns total heating value
    """
    # Assuming heating value is proportional to temperature integral
    return np.trapz(temperatures, positions)

def calculate_nox_emissions(temperature, C1, C2):
    """
    Calculate NOx emissions using fitted equation
    """
    # Scale temperature to avoid overflow
    T_scaled = (temperature - 1000) / 100  # Center around typical combustion temperature
    return C1 * np.exp(C2 * T_scaled)

def calculate_fitness(temperature, nox, alpha):
    """
    Calculate fitness value using the formula F = T - alpha*NOx
    """
    # Scale the values to similar ranges
    T_scaled = temperature / 1000  # Scale temperature to thousands
    NOx_scaled = nox * 1e6  # Scale NOx to ppm
    return T_scaled - alpha * NOx_scaled 