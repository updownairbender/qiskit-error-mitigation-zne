"""Noise levels maker"""

import qiskit_aer.noise as noise
from numpy import arange # strange import style, but maybe more efficient


def create_bit_flip_noise(error_probability: float) -> noise.NoiseModel:
    """
    Creates a Qiskit Aer noise model simulating a quantum bit-flip error.

    Args:
        error_probability (float): Probability of a bit-flip occurring (0.0 to 1.0).

    Returns:
        qiskit_aer.noise.NoiseModel: Configured noise model for simulation.

    Implementation Details:
        The noise model targets the following modern Qiskit 2.x quantum instructions:
        - 'x': The active bit-flip gate, ensuring operations are noisy.
        - 'u': The universal single-qubit rotation gate (replacing the deprecated 'u3'),
               capturing compiled superposition gates like the Hadamard gate.
        - 'id': The identity/idle gate, simulating noise and decoherence 
                that occurs while a qubit is sitting idle.
    """
    # 1. Define the error type: a Pauli-X gate represents a bit-flip error
    bit_flip_error = noise.pauli_error([('X', error_probability), ('I', 1 - error_probability)])
    
    # 2. Initialize the noise model container
    noise_model = noise.NoiseModel()
    
    # 3. Instruct the model to apply this error to target quantum gates
    noise_model.add_all_qubit_quantum_error(bit_flip_error, ['u', 'x', 'id'])
    
    return noise_model

def get_noise_levels(base_error_probability: float, range_start: int = 1, range_end: int = 5) -> tuple:
    """
    Generates scaled noise models (1x and 2x) required for Zero-Noise Extrapolation (ZNE).

    Args:
        base_error_probability (float): Baseline noise probability.
        range_start (int): Starting point for the noise level range.
        range_end (int): Ending point for the noise level range.

    Returns:
        tuple: A pair of Qiskit noise models (1x noise, 2x noise).
    """
    x = arange(range_start, range_end + 1) * base_error_probability
    y = map(create_bit_flip_noise, x)
    
    return zip(x, y)
