"""
Domain event base class.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class DomainEvent:
    """Base class for all domain events."""
    
    event_id: str
    event_type: str
    aggregate_id: str
    timestamp: datetime
    data: Any
    
    def __init__(self, event_type: str, aggregate_id: str, data: Any):
        self.event_type = event_type
        self.aggregate_id = aggregate_id
        self.timestamp = datetime.now()
        self.data = data
