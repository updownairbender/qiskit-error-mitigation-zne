"""Error mitigation module for quantum circuits using Zero Noise Extrapolation (ZNE) method."""

import os
import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from sklearn.linear_model import LinearRegression

from .noise_maker import get_noise_levels

TOTAL_SHOTS = 1024
DESIRED_OUTCOME = '111'  # For GHZ state, perfect prob for outcome '111' is 50%
PERFECT_PROB = 0.50      # Ideal quantum mechanical probability for the state


def collect_noisy_probabilities(circuit: QuantumCircuit, noise_levels: list, target_state: str) -> tuple[list[list[float]], list[float]]:
    """
    Executes a quantum circuit across various noise levels to collect outcome probabilities.

    Args:
        circuit (QuantumCircuit): The quantum circuit to simulate.
        noise_levels (list): List of tuples containing (noise_scale, NoiseModel).
        target_state (str): The specific bitstring outcome to track.

    Returns:
        tuple: A pair of lists (X, y) where X contains features [[scale], ...] 
               and y contains target probabilities [prob, ...].
    """
    X = []
    y = []
    
    for noise_scale, noise_model in noise_levels:
        backend = AerSimulator(noise_model=noise_model)
        job = backend.run(circuit, shots=TOTAL_SHOTS)
        counts = job.result().get_counts()
        
        # Safe extraction to handle heavy noise scaling safely
        prob = counts.get(target_state, 0) / TOTAL_SHOTS
        
        X.append([noise_scale])
        y.append(prob)
        
    return X, y


def generate_zne_plot(X: list[list[float]], y: list[float], model: LinearRegression, zero_noise_val: float, target_state: str, output_dir: str = "plots", filename: str = "zne_mitigation_plot.png"):
    """
    Generates, saves, and displays an inline publication-quality Zero-Noise Extrapolation plot.

    Args:
        X (list): Noise factors evaluated.
        y (list): Measured raw probabilities.
        model (LinearRegression): Trained classical regression model.
        zero_noise_val (float): Extrapolated zero-noise intercept value.
        target_state (str): Tracked quantum state bitstring.
        output_dir (str): Target directory where the plot will be saved.
        filename (str): Target filename for saving the plot graph image.
    """
    # Create the directory if it does not exist
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Create a figure object explicitly
    fig = plt.figure(figsize=(8, 5))
    
    # Plot raw noisy experimental runs
    scatter_noisy = plt.scatter(X, y, color='red', marker='o', zorder=3, label='Noisy Data Points (Simulated)')
    
    # Generate continuous extrapolation trendline backward through zero axis
    max_noise = max(X)[0] if X else 1.0
    X_plot = np.linspace(0, max_noise, 100).reshape(-1, 1)
    y_plot = model.predict(X_plot)
    
    # Plot the line representing the linear regression fit
    line_fit = plt.plot(X_plot, y_plot, color='blue', linestyle='--', label='Linear Extrapolation Fit')[0]
    
    # Highlight calculated ideal point
    scatter_mitigated = plt.scatter([0], [zero_noise_val], color='green', marker='*', s=150, zorder=4,
                                   label=f'Mitigated Value (Zero Noise): {zero_noise_val:.3f}')
    
    # Draw a horizontal reference line showing the true ideal mathematical limit
    line_target = plt.axhline(y=PERFECT_PROB, color='purple', linestyle=':', alpha=0.7, 
                              label=f'Theoretical Target ({PERFECT_PROB:.2f})')
    
    # Graph formatting
    plt.title(f"Zero-Noise Extrapolation (ZNE) for Outcome '{target_state}'")
    plt.xlabel("Noise Factor (Scale)")
    plt.ylabel(f"Probability of State |{target_state}>")
    
    # --- DYNAMIC AXIS SCALING ---
    plt.xlim(left=-0.2, right=max_noise + 0.3)
    
    all_y_elements = y + [zero_noise_val, PERFECT_PROB] + list(y_plot)
    y_min, y_max = min(all_y_elements), max(all_y_elements)
    padding = max(0.05, (y_max - y_min) * 0.15)
    plt.ylim(bottom=max(0.0, y_min - padding), top=min(1.0, y_max + padding))
    
    plt.grid(True, linestyle=':', alpha=0.6)
    
    # Explicitly order the handles and labels for the legend
    handles = [scatter_noisy, scatter_mitigated, line_fit, line_target]
    labels = [h.get_label() for h in handles]
    plt.legend(handles, labels)
    
    # Construct final file destination path safely and save
    save_path = os.path.join(output_dir, filename)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def mitigate_circuit(circuit: QuantumCircuit, base_error_probability: float, range_start: int = 1, range_end: int = 5) -> float:
    """
    Mitigates the noise in a quantum circuit using Zero Noise Extrapolation (ZNE).

    Args:
        circuit (QuantumCircuit): The quantum circuit to be mitigated.
        base_error_probability (float): Baseline noise probability.
        range_start (int): Starting point for the noise level range.
        range_end (int): Ending point for the noise level range.

    Returns:
        float: Calculated ideal expectation probability at zero noise.
    """
    # 1. Generate scaled noise configuration spaces
    noise_levels = get_noise_levels(base_error_probability, range_start, range_end)
    
    # 2. Extract dataset via simulator execution tracking
    X, y = collect_noisy_probabilities(circuit, noise_levels, DESIRED_OUTCOME)
    
    # 3. Fit classical machine learning model
    model = LinearRegression()
    model.fit(X, y)
    
    # 4. Infer theoretical ideal baseline value
    zero_noise_result = float(model.predict([[0.0]])[0])
    
    # 5. Render asset visualization (defaults to saving in the 'plots' folder)
    generate_zne_plot(X, y, model, zero_noise_result, DESIRED_OUTCOME)
    
    return zero_noise_result
    