import asyncio
import logging
from typing import Dict, Any, Optional, Callable
from abc import ABC, abstractmethod
from backend.app.blackboard import Blackboard, global_blackboard
from backend.app.config import settings

logger = logging.getLogger(__name__)

class UniverseAgent(ABC):
    """
    Abstract base class for a parallel universe browser agent.
    Runs isolated browser navigation according to its unique heuristic strategy,
    communicates discoveries with the blackboard, and yields live telemetry events.
    """
    def __init__(
        self,
        universe_id: str,
        name: str,
        strategy_description: str,
        blackboard: Optional[Blackboard] = None,
        event_callback: Optional[Callable[[Dict[str, Any]], Any]] = None
    ):
        self.universe_id = universe_id
        self.name = name
        self.strategy_description = strategy_description
        self.blackboard = blackboard or global_blackboard
        self.event_callback = event_callback
        
        self.step_count = 0
        self.max_steps = settings.MAX_STEPS_PER_UNIVERSE
        self.is_active = True
        self.current_price: Optional[float] = None
        self.evidence_screenshots: list[str] = []
        self.findings: Dict[str, Any] = {}

    async def emit_event(
        self,
        action: str,
        target_url: str = "",
        screenshot_b64: str = "",
        found_price: Optional[float] = None,
        status: str = "running",
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.step_count += 1
        event = {
            "universe": self.universe_id,
            "universe_name": self.name,
            "step": self.step_count,
            "action": action,
            "target_url": target_url,
            "screenshot": screenshot_b64,
            "found_price": found_price if found_price is not None else self.current_price,
            "status": status,
            "metadata": metadata or {}
        }
        if self.event_callback:
            if asyncio.iscoroutinefunction(self.event_callback):
                await self.event_callback(event)
            else:
                self.event_callback(event)
        return event

    @abstractmethod
    async def run(self, query: str, target_urls: list[str]):
        """Executes the universe's autonomous strategy"""
        pass
