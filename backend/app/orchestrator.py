import asyncio
import logging
from typing import Dict, Any, List, Callable, Optional
from backend.app.blackboard import Blackboard
from backend.app.universes.budget import BudgetUniverse
from backend.app.universes.deal_hunter import DealHunterUniverse
from backend.app.universes.trust import TrustUniverse
from backend.app.universes.value import BestValueUniverse
from backend.app.integrations.aws_client import aws_client
from backend.app.integrations.elevenlabs_voice import elevenlabs_client

logger = logging.getLogger(__name__)

class MultiverseOrchestrator:
    """
    Coordinates the parallel universe swarm race.
    1. Spawns isolated browser agents with different objective functions.
    2. Synchronizes intelligence through the shared Blackboard.
    3. Streams real-time events to connected WebSocket clients.
    4. Triggers AWS Bedrock Judge to aggregate receipts into a final verdict.
    """
    def __init__(self, event_callback: Optional[Callable[[Dict[str, Any]], Any]] = None):
        self.blackboard = Blackboard()
        self.event_callback = event_callback
        self.is_running = False

    async def execute_run(self, goal: str, target_urls: List[str]) -> Dict[str, Any]:
        self.is_running = True
        
        await self._broadcast({
            "type": "ORCHESTRATOR_START",
            "goal": goal,
            "target_urls": target_urls,
            "message": "Initializing 4 Parallel Universes: Budget, Deal Hunter, Trust, and Best Value."
        })

        # Initialize the 4 universes
        universes = [
            BudgetUniverse(blackboard=self.blackboard, event_callback=self._broadcast),
            DealHunterUniverse(blackboard=self.blackboard, event_callback=self._broadcast),
            TrustUniverse(blackboard=self.blackboard, event_callback=self._broadcast),
            BestValueUniverse(blackboard=self.blackboard, event_callback=self._broadcast),
        ]

        # Run universes concurrently
        tasks = [u.run(goal, target_urls) for u in universes]
        await asyncio.gather(*tasks)

        # Synthesize final verdict via AWS Bedrock Judge
        await self._broadcast({
            "type": "JUDGE_EVALUATING",
            "message": "Universes finished browsing. Multiverse Judge (Bedrock LLM) synthesizing receipts..."
        })
        await asyncio.sleep(1.0)

        verdict = await aws_client.invoke_judge(
            goal=goal,
            universe_reports=[{"id": u.universe_id, "findings": u.findings} for u in universes],
            dark_patterns=self.blackboard.dark_patterns
        )

        # Generate ElevenLabs spoken verdict
        audio_info = await elevenlabs_client.generate_verdict_audio(verdict["spoken_summary"])
        verdict["audio"] = audio_info

        await self._broadcast({
            "type": "VERDICT_FINALIZED",
            "verdict": verdict
        })

        self.is_running = False
        return verdict

    async def _broadcast(self, event: Dict[str, Any]):
        if self.event_callback:
            if asyncio.iscoroutinefunction(self.event_callback):
                await self.event_callback(event)
            else:
                self.event_callback(event)
