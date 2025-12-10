"""Event bus port interface."""

from abc import ABC, abstractmethod
from typing import Dict, Callable
from ...domain.event import DomainEvent


class EventBusPort(ABC):
    """Port for event-driven communication."""
    
    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """Publish event."""
        pass
    
    @abstractmethod
    async def subscribe(self, event_type: str, handler: Callable) -> str:
        """Subscribe to event type, returns subscription_id."""
        pass
    
    @abstractmethod
    async def unsubscribe(self, subscription_id: str) -> None:
        """Unsubscribe."""
        pass


