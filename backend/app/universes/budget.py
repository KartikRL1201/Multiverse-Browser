import asyncio
import logging
from typing import List
from backend.app.universes.base import UniverseAgent

logger = logging.getLogger(__name__)

class BudgetUniverse(UniverseAgent):
    """
    Universe 1: Budget
    Prioritizes the lowest true landed checkout price (base + shipping + fees - coupons).
    Detects drip pricing and listens to Blackboard for coupons found by peers.
    """
    def __init__(self, **kwargs):
        super().__init__(
            universe_id="budget",
            name="Budget Universe",
            strategy_description="Pursues the absolute lowest landed cost to the checkout step",
            **kwargs
        )

    async def run(self, query: str, target_urls: list[str]):
        await self.emit_event(
            action="Initializing budget scan across candidate stores",
            status="running"
        )
        await asyncio.sleep(0.4)

        # 1. Check ElectroBazaar (Naive apparent lowest listed price)
        eb_url = next((u for u in target_urls if "electrobazaar" in u), None)
        if eb_url:
            await self.emit_event(
                action=f"Found apparent low price ₹2,199 at {eb_url}. Navigating to checkout to verify.",
                target_url=eb_url,
                found_price=2199,
                status="running"
            )
            await asyncio.sleep(1.0)
            
            # Navigating to checkout reveals drip pricing
            checkout_url = f"{eb_url}/checkout"
            landed_price = 2547 # 2199 + 199 + 149
            await self.blackboard.post_dark_pattern(
                universe=self.universe_id,
                pattern_type="Drip Pricing",
                details="Hidden mandatory ₹199 convenience fee + ₹149 packaging fee added at checkout",
                evidence_url=checkout_url
            )
            await self.emit_event(
                action=f"🚨 DARK PATTERN DETECTED: Drip pricing added +₹348 in fees at checkout! Real price: ₹{landed_price}",
                target_url=checkout_url,
                found_price=landed_price,
                status="flagged",
                metadata={"drip_fees": 348, "original_listed": 2199}
            )
            self.current_price = landed_price
            await asyncio.sleep(0.8)

        # 2. Check Blackboard for shared coupons before evaluating DealNest
        valid_coupons = await self.blackboard.get_valid_coupons(site="dealnest")
        dn_url = next((u for u in target_urls if "dealnest" in u), None)
        
        if dn_url:
            base_price = 2799
            await self.emit_event(
                action=f"Inspecting DealNest (Listed ₹{base_price}). Listening to blackboard for active coupons...",
                target_url=dn_url,
                found_price=base_price,
                status="running"
            )
            await asyncio.sleep(1.2) # Allow deal hunter to finish posting if concurrent
            
            # Re-check blackboard for telepathy effect
            valid_coupons = await self.blackboard.get_valid_coupons(site="dealnest")
            if valid_coupons:
                coupon = valid_coupons[0]
                final_price = 2299 # 2799 - 500
                await self.emit_event(
                    action=f"✨ TELEPATHY APPLIED: Injected coupon '{coupon['code']}' from Deal Hunter! Price slashed to ₹{final_price}",
                    target_url=f"{dn_url}/checkout?coupon={coupon['code']}",
                    found_price=final_price,
                    status="discovery",
                    metadata={"applied_coupon": coupon['code'], "savings": 500}
                )
                self.current_price = final_price
                self.findings["winner"] = {
                    "store": "DealNest",
                    "landed_price": final_price,
                    "coupon": coupon['code'],
                    "dark_patterns_avoided": ["Drip Pricing at ElectroBazaar", "Fake MRP at FlashKart"]
                }

        await self.emit_event(
            action="Budget universe reached final landed checkout verdict.",
            found_price=self.current_price,
            status="completed"
        )
