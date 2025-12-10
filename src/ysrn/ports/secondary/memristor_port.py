"""Memristor port interface."""

from abc import ABC, abstractmethod
import numpy as np


class MemristorPort(ABC):
    """Port for memristor hardware/simulation."""
    
    @abstractmethod
    def read_resistance(self, index: int) -> float:
        """Read resistance at index."""
        pass
    
    @abstractmethod
    def write_resistance(self, index: int, 
                        target_r: float) -> None:
        """Write target resistance."""
        pass
    
    @abstractmethod
    def apply_voltage_pulse(self, index: int,
                           voltage: float, 
                           duration: float) -> float:
        """Apply voltage pulse, returns new resistance."""
        pass
    
    @abstractmethod
    def get_all_weights(self) -> np.ndarray:
        """Get all constraint weights."""
        pass


