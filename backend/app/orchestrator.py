import asyncio
import logging
from typing import Dict, Any, List, Callable, Optional
from playwright.async_api import async_playwright

from backend.app.blackboard import Blackboard
from backend.app.planner import StrategyPlanner
from backend.app.universes.dynamic_worker import DynamicUniverseWorker
from backend.app.integrations.aws_client import aws_client
from backend.app.integrations.elevenlabs_voice import elevenlabs_client

logger = logging.getLogger(__name__)


class MultiverseOrchestrator:
    """
    Coordinates a dynamic parallel universe swarm for ANY web goal:
    1. Strategy Planner determines how many universes (N) are needed and assigns heuristics.
    2. Spawns N isolated Playwright browser sessions concurrently.
    3. Synchronizes discoveries (vouchers, drip fees, eligibility, deadlines, fine print) on the Blackboard.
    4. Streams live telemetry & screenshot receipts via WebSockets.
    5. Triggers Judge to synthesize receipts into one verified verdict.
    """

    def __init__(
        self,
        event_callback: Optional[Callable[[Dict[str, Any]], Any]] = None,
        base_url: Optional[str] = None,
    ):
        self.blackboard = Blackboard()
        self.event_callback = event_callback
        self.planner = StrategyPlanner(base_url=base_url)
        self.is_running = False

    async def execute_run(self, goal: str, target_urls: Optional[List[str]] = None) -> Dict[str, Any]:
        self.is_running = True

        # 1. Dynamically plan how many universes are needed
        plan = await self.planner.create_plan(goal=goal, target_urls=target_urls)

        await self._broadcast({
            "type": "PLAN_GENERATED",
            "goal": plan.goal,
            "domain": plan.domain,
            "universe_count": plan.universe_count,
            "reasoning": plan.reasoning,
            "universes": [u.model_dump() for u in plan.universes],
            "target_urls": plan.target_urls,
        })

        # 2. Spawn N parallel workers inside an async Playwright Chromium runtime
        workers: List[DynamicUniverseWorker] = []
        playwright_ctx = None
        browser = None

        try:
            try:
                playwright_ctx = await async_playwright().start()
                browser = await playwright_ctx.chromium.launch(headless=True)
            except Exception as pw_err:
                logger.warning(f"Playwright browser unavailable, falling back to lightweight mode: {pw_err}")
                browser = None

            workers = [
                DynamicUniverseWorker(
                    spec=spec,
                    blackboard=self.blackboard,
                    event_callback=self._broadcast,
                    browser=browser,
                )
                for spec in plan.universes
            ]

            await asyncio.gather(*(w.run(plan.goal, plan.target_urls) for w in workers))
        finally:
            if browser is not None:
                await browser.close()
            if playwright_ctx is not None:
                await playwright_ctx.stop()

        # 3. Synthesize final verdict via Judge
        await self._broadcast({
            "type": "JUDGE_EVALUATING",
            "message": f"All {plan.universe_count} universes finished. Judge synthesizing evidence & blackboard findings...",
        })
        await asyncio.sleep(0.4)

        verdict = await aws_client.invoke_judge(
            goal=plan.goal,
            domain=plan.domain,
            universe_count=plan.universe_count,
            universe_reports=[{"id": w.universe_id, **w.findings} for w in workers],
            dark_patterns=self.blackboard.dark_patterns,
            coupons=self.blackboard.coupons,
            findings=self.blackboard.findings,
        )

        # 4. Generate ElevenLabs spoken verdict
        audio_info = await elevenlabs_client.generate_verdict_audio(verdict["spoken_summary"])
        verdict["audio"] = audio_info

        await self._broadcast({
            "type": "VERDICT_FINALIZED",
            "verdict": verdict,
        })

        self.is_running = False
        return verdict

    async def _broadcast(self, event: Dict[str, Any]):
        if self.event_callback:
            if asyncio.iscoroutinefunction(self.event_callback):
                await self.event_callback(event)
            else:
                self.event_callback(event)
