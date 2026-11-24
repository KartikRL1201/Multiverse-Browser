import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

class Blackboard:
    """
    Shared intelligence board for parallel universe browser agents.
    Allows agents to share coupons, pricing truths, dark pattern alerts,
    and dead-end warnings in real-time.
    """
    def __init__(self):
        self._lock = asyncio.Lock()
        self.coupons: Dict[str, Dict[str, Any]] = {}
        self.dark_patterns: List[Dict[str, Any]] = []
        self.price_discoveries: List[Dict[str, Any]] = []
        self.dead_ends: List[str] = []
        self.events_log: List[Dict[str, Any]] = []
        self._subscribers: List[asyncio.Queue] = []

    async def post_coupon(self, universe: str, code: str, discount_text: str, site: str):
        async with self._lock:
            entry = {
                "universe": universe,
                "code": code,
                "discount_text": discount_text,
                "site": site,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.coupons[code] = entry
            await self._broadcast({"type": "COUPON_DISCOVERED", **entry})

    async def post_dark_pattern(self, universe: str, pattern_type: str, details: str, evidence_url: str = ""):
        async with self._lock:
            entry = {
                "universe": universe,
                "pattern_type": pattern_type,
                "details": details,
                "evidence_url": evidence_url,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.dark_patterns.append(entry)
            await self._broadcast({"type": "DARK_PATTERN_FLAGGED", **entry})

    async def post_price(self, universe: str, store: str, item_name: str, listed_price: float, checkout_price: float):
        async with self._lock:
            entry = {
                "universe": universe,
                "store": store,
                "item_name": item_name,
                "listed_price": listed_price,
                "checkout_price": checkout_price,
                "difference": checkout_price - listed_price,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.price_discoveries.append(entry)
            await self._broadcast({"type": "PRICE_UPDATED", **entry})

    async def get_valid_coupons(self, site: Optional[str] = None) -> List[Dict[str, Any]]:
        async with self._lock:
            if site:
                return [c for c in self.coupons.values() if c["site"] == site or not c["site"]]
            return list(self.coupons.values())

    async def subscribe(self) -> asyncio.Queue:
        q = asyncio.Queue()
        self._subscribers.append(q)
        return q

    async def unsubscribe(self, q: asyncio.Queue):
        if q in self._subscribers:
            self._subscribers.remove(q)

    async def _broadcast(self, event: Dict[str, Any]):
        self.events_log.append(event)
        for q in self._subscribers:
            await q.put(event)

# Global blackboard instance for runs
global_blackboard = Blackboard()
