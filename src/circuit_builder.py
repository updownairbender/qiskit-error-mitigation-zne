"""Circuit builder"""

from qiskit import QuantumCircuit


def GHZ_state_circuit():
    """GHZ state circuit."""
    circuit = QuantumCircuit(3, 3)

    circuit.h(0)
    circuit.cx(0, 1)
    circuit.cx(1, 2)

    circuit.measure([0, 1, 2], [0, 1, 2])

    return circuit
