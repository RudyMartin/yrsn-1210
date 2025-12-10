"""In-memory event bus adapter for testing."""

from typing import Dict, List, Tuple, Callable
import asyncio
import logging
from ....ports.secondary.event_bus_port import EventBusPort
from ....domain.event import DomainEvent

logger = logging.getLogger(__name__)


class InMemoryEventBusAdapter(EventBusPort):
    """In-memory event bus for testing."""
    
    def __init__(self):
        self.handlers: Dict[str, List[Tuple[str, Callable]]] = {}
    
    async def publish(self, event: DomainEvent) -> None:
        handlers = self.handlers.get(event.event_type, [])
        for _, handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"Event handler error: {e}")
    
    async def subscribe(self, event_type: str,
                       handler: Callable) -> str:
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        
        import uuid
        sub_id = str(uuid.uuid4())
        self.handlers[event_type].append((sub_id, handler))
        return sub_id
    
    async def unsubscribe(self, subscription_id: str) -> None:
        for event_type in self.handlers:
            self.handlers[event_type] = [
                (sid, h) for sid, h in self.handlers[event_type]
                if sid != subscription_id
            ]


