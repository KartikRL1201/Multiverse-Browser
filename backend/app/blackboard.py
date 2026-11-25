import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone


class Blackboard:
    """
    Shared intelligence board for parallel universe browser agents.
    Domain-agnostic cross-agent memory: agents publish and subscribe to
    vouchers, drip fees, fake claims, fine-print traps, eligibility rules,
    deadlines, dead-ends, and verified options in real time.
    """

    def __init__(self):
        self._lock = asyncio.Lock()
        self.coupons: Dict[str, Dict[str, Any]] = {}
        self.dark_patterns: List[Dict[str, Any]] = []
        self.price_discoveries: List[Dict[str, Any]] = []
        self.findings: List[Dict[str, Any]] = []
        self.dead_ends: List[str] = []
        self.events_log: List[Dict[str, Any]] = []
        self._subscribers: List[asyncio.Queue] = []

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    async def post_finding(
        self,
        universe: str,
        category: str,
        title: str,
        details: str,
        severity: str = "info",
        evidence_url: str = "",
        site: str = "",
        data: Optional[Dict[str, Any]] = None,
    ):
        """Publish any general discovery (catch, fine print, eligibility, deadline, perk)."""
        async with self._lock:
            entry = {
                "universe": universe,
                "category": category.upper(),
                "title": title,
                "details": details,
                "severity": severity,
                "evidence_url": evidence_url,
                "site": site,
                "data": data or {},
                "timestamp": self._now_iso(),
            }
            self.findings.append(entry)
            await self._broadcast({"type": "BLACKBOARD_FINDING", **entry})

    async def get_findings(
        self, category: Optional[str] = None, site: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        async with self._lock:
            res = self.findings
            if category:
                cat_up = category.upper()
                res = [f for f in res if f["category"] == cat_up]
            if site:
                res = [f for f in res if f["site"] == site or not f["site"]]
            return list(res)

    async def post_coupon(self, universe: str, code: str, discount_text: str, site: str):
        async with self._lock:
            entry = {
                "universe": universe,
                "code": code,
                "discount_text": discount_text,
                "site": site,
                "timestamp": self._now_iso(),
            }
            self.coupons[code] = entry
            self.findings.append({
                "universe": universe,
                "category": "VOUCHER",
                "title": f"Promo code {code}",
                "details": f"{code} ({discount_text}) on {site}",
                "severity": "positive",
                "site": site,
                "data": {"code": code, "discount_text": discount_text},
                "timestamp": entry["timestamp"],
            })
            await self._broadcast({"type": "COUPON_DISCOVERED", **entry})

    async def post_dark_pattern(
        self, universe: str, pattern_type: str, details: str, evidence_url: str = "", site: str = ""
    ):
        async with self._lock:
            entry = {
                "universe": universe,
                "pattern_type": pattern_type,
                "details": details,
                "evidence_url": evidence_url,
                "site": site,
                "timestamp": self._now_iso(),
            }
            self.dark_patterns.append(entry)
            self.findings.append({
                "universe": universe,
                "category": "CATCH_FLAGGED",
                "title": pattern_type,
                "details": details,
                "severity": "high",
                "evidence_url": evidence_url,
                "site": site,
                "data": {"pattern_type": pattern_type},
                "timestamp": entry["timestamp"],
            })
            await self._broadcast({"type": "DARK_PATTERN_FLAGGED", **entry})

    async def post_price(
        self, universe: str, store: str, item_name: str, listed_price: float, checkout_price: float
    ):
        async with self._lock:
            entry = {
                "universe": universe,
                "store": store,
                "item_name": item_name,
                "listed_price": listed_price,
                "checkout_price": checkout_price,
                "difference": checkout_price - listed_price,
                "timestamp": self._now_iso(),
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
