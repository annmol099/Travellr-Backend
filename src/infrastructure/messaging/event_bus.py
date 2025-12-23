"""
Event bus for domain event publishing.
"""
from typing import Callable, List, Dict


class EventBus:
    """Event bus for publishing and subscribing to domain events."""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to an event type."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
    
    def publish(self, event):
        """Publish an event to all subscribers."""
        event_type = event.event_type
        if event_type in self.subscribers:
            for handler in self.subscribers[event_type]:
                handler(event)
    
    def unsubscribe(self, event_type: str, handler: Callable):
        """Unsubscribe from an event type."""
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(handler)
