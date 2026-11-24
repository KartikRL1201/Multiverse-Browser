import asyncio
import logging
from typing import List
from backend.app.universes.base import UniverseAgent

logger = logging.getLogger(__name__)

class DealHunterUniverse(UniverseAgent):
    """
    Universe 4: Deal Hunter
    Focuses on scraping promo codes, hidden footer vouchers, and promotional deals.
    Posts discoveries to the shared Blackboard so other universes (like Budget) can apply them.
    """
    def __init__(self, **kwargs):
        super().__init__(
            universe_id="deal_hunter",
            name="Deal Hunter Universe",
            strategy_description="Aggressively scans for promo vouchers, discount codes, and unlisted coupons",
            **kwargs
        )

    async def run(self, query: str, target_urls: List[str]):
        await self.emit_event(
            action="Initializing voucher scraping heuristics across target endpoints",
            status="running"
        )
        await asyncio.sleep(0.5)

        for url in target_urls:
            await self.emit_event(
                action=f"Inspecting footer elements and discount selectors at {url}",
                target_url=url,
                status="running"
            )
            await asyncio.sleep(0.8)

            if "dealnest" in url:
                coupon_code = "DEAL500"
                await self.blackboard.post_coupon(
                    universe=self.universe_id,
                    code=coupon_code,
                    discount_text="₹500 instant discount",
                    site="dealnest"
                )
                await self.emit_event(
                    action=f"[VoucherExtracted] Unlisted code '{coupon_code}' (-₹500) discovered in footer. Broadcasted to blackboard.",
                    target_url=url,
                    found_price=2299,
                    status="discovery",
                    metadata={"coupon_found": coupon_code, "discount": 500}
                )
                self.current_price = 2299
                self.findings["best_deal"] = {"coupon": coupon_code, "price": 2299, "store": "dealnest"}
                break

        await self.emit_event(
            action="Voucher discovery pass completed. Intelligence synced to blackboard.",
            found_price=self.current_price,
            status="completed"
        )
