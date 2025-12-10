"""Sensor port interface."""

from abc import ABC, abstractmethod
from typing import List, Dict, Callable


class SensorPort(ABC):
    """Port for sensor data acquisition."""
    
    @abstractmethod
    def read_sensor(self, sensor_id: str) -> Dict:
        """Read current sensor value."""
        pass
    
    @abstractmethod
    def subscribe(self, sensor_id: str, 
                 callback: Callable) -> str:
        """Subscribe to sensor updates, returns subscription_id."""
        pass
    
    @abstractmethod
    def unsubscribe(self, subscription_id: str) -> None:
        """Unsubscribe from sensor."""
        pass
    
    @abstractmethod
    def list_sensors(self) -> List[Dict]:
        """List available sensors."""
        pass


