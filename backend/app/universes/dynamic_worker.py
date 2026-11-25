import asyncio
import base64
import logging
import re
from typing import List, Dict, Any, Optional, Callable
from urllib.parse import urlparse

from playwright.async_api import Browser, Page
from backend.app.blackboard import Blackboard
from backend.app.config import settings
from backend.app.planner import UniverseSpec
from backend.app.universes.base import UniverseAgent

logger = logging.getLogger(__name__)


class DynamicUniverseWorker(UniverseAgent):
    """
    Goal-agnostic parallel browser worker.
    Executes a dynamically planned UniverseSpec inside an isolated Playwright context,
    reads real DOM nodes & fine print, captures screenshot receipts, and exchanges
    discoveries with peer universes via the Shared Blackboard.
    """

    def __init__(
        self,
        spec: UniverseSpec,
        blackboard: Blackboard,
        event_callback: Optional[Callable[[Dict[str, Any]], Any]] = None,
        browser: Optional[Browser] = None,
    ):
        super().__init__(
            universe_id=spec.universe_id,
            name=spec.title,
            strategy_description=spec.strategy,
            blackboard=blackboard,
            event_callback=event_callback,
        )
        self.spec = spec
        self.browser = browser
        self.metric_display: str = "--"
        self.findings["role"] = spec.role
        self.findings["focus_type"] = spec.focus_type
        self.findings["sites_audited"] = []

    def _is_allowed_url(self, url: str) -> bool:
        parsed = urlparse(url)
        return parsed.hostname in ("localhost", "127.0.0.1")

    async def _snap(self, page: Page) -> str:
        try:
            raw = await page.screenshot(type="jpeg", quality=55)
            return "data:image/jpeg;base64," + base64.b64encode(raw).decode("ascii")
        except Exception:
            return ""

    async def emit_dynamic(
        self,
        action: str,
        target_url: str = "",
        screenshot_b64: str = "",
        metric_text: Optional[str] = None,
        found_price: Optional[float] = None,
        status: str = "running",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        if metric_text is not None:
            self.metric_display = metric_text
        meta = dict(metadata or {})
        meta["metric_display"] = self.metric_display
        meta["metric_label"] = self.spec.metric_label
        return await self.emit_event(
            action=action,
            target_url=target_url,
            screenshot_b64=screenshot_b64,
            found_price=found_price,
            status=status,
            metadata=meta,
        )

    async def run(self, query: str, target_urls: List[str]):
        urls = target_urls or self.spec.target_urls
        await self.emit_dynamic(
            action=f"Initializing isolated session · Strategy: {self.spec.role}",
            status="running",
        )

        if self.browser is None:
            await self._run_simulated_fallback(urls)
            return

        context = await self.browser.new_context(viewport={"width": 960, "height": 620})
        page = await context.new_page()

        try:
            # Slight stagger for voucher hunters vs landed_cost auditors so blackboard sync shines naturally
            if self.spec.focus_type in ("landed_cost", "value_matrix"):
                await asyncio.sleep(0.35)

            for url in urls:
                if self.step_count >= settings.MAX_STEPS_PER_UNIVERSE:
                    await self.emit_dynamic(
                        action="Step budget reached (15/15). Halting safely.",
                        status="completed",
                    )
                    break

                if not self._is_allowed_url(url):
                    await self.emit_dynamic(
                        action=f"Blocked navigation outside domain allowlist: {url}",
                        target_url=url,
                        status="flagged",
                    )
                    continue

                await self.emit_dynamic(
                    action=f"Navigating to {url.replace('http://127.0.0.1:8000', '')}",
                    target_url=url,
                    status="running",
                )

                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=8000)
                except Exception as nav_err:
                    await self.emit_dynamic(
                        action=f"Endpoint unreachable ({str(nav_err).splitlines()[0]}), skipping.",
                        target_url=url,
                        status="running",
                    )
                    continue

                shot = await self._snap(page)
                title_text = (await page.title()).strip()
                self.findings["sites_audited"].append({"url": url, "title": title_text})

                await self._inspect_page_by_focus(page, url, shot)
                await asyncio.sleep(0.25)

            await self.emit_dynamic(
                action=f"{self.spec.title} finished audit across {len(self.findings['sites_audited'])} endpoints.",
                metric_text=self.metric_display,
                status="completed",
            )
        finally:
            await context.close()

    async def _inspect_page_by_focus(self, page: Page, url: str, shot: str):
        focus = self.spec.focus_type
        site_slug = self._extract_site_slug(url)

        # 1. VOUCHER / PERK HUNTING
        if focus == "voucher_hunt":
            promo_el = await page.query_selector("[data-coupon], #coupon-code")
            if promo_el:
                code_attr = await promo_el.get_attribute("data-coupon")
                code_text = (await promo_el.inner_text()).strip()
                code = (code_attr or code_text).strip()
                banner_el = await page.query_selector("#promo-banner")
                banner_txt = (await banner_el.inner_text()).strip() if banner_el else f"Code {code}"

                await self.blackboard.post_coupon(
                    universe=self.universe_id,
                    code=code,
                    discount_text=banner_txt,
                    site=site_slug,
                )
                await self.emit_dynamic(
                    action=f"[BlackboardWrite] Extracted '{code}' on {site_slug}. Broadcasted to peer universes.",
                    target_url=url,
                    screenshot_b64=shot,
                    metric_text=code,
                    status="discovery",
                    metadata={"coupon": code, "site": site_slug},
                )
                self.findings["voucher"] = {"code": code, "site": site_slug, "details": banner_txt}
            else:
                await self.emit_dynamic(
                    action=f"Scanned footer & banners on {site_slug}: no unlisted vouchers found.",
                    target_url=url,
                    screenshot_b64=shot,
                    status="running",
                )
            return

        # 2. FINE PRINT / ELIGIBILITY / TRUST AUDIT
        if focus in ("fine_print", "eligibility"):
            catch_els = await page.query_selector_all(".catch-box")
            mrp_el = await page.query_selector("#mrp-section")
            body_text = await page.inner_text("body")

            if catch_els:
                for cel in catch_els:
                    ctype = (await cel.get_attribute("data-catch-type")) or "FINE_PRINT"
                    ctext = re.sub(r"\s+", " ", (await cel.inner_text()).strip())
                    await self.blackboard.post_dark_pattern(
                        universe=self.universe_id,
                        pattern_type=ctype,
                        details=f"[{site_slug}] {ctext}",
                        evidence_url=url,
                        site=site_slug,
                    )
                    await self.emit_dynamic(
                        action=f"[{ctype}] {ctext[:110]}",
                        target_url=url,
                        screenshot_b64=shot,
                        metric_text="Trap Flagged",
                        status="flagged",
                    )
                self.findings.setdefault("catches", []).append(site_slug)
            elif mrp_el and "not manufacturer verified" in (await mrp_el.inner_text()).lower():
                await self.blackboard.post_dark_pattern(
                    universe=self.universe_id,
                    pattern_type="FAKE_MRP",
                    details=f"[{site_slug}] Unverified anchor MRP claimed to inflate discount percentage.",
                    evidence_url=url,
                    site=site_slug,
                )
                await self.emit_dynamic(
                    action=f"[FakeMRPFlagged] {site_slug} claims unverified MRP to fabricate discount.",
                    target_url=url,
                    screenshot_b64=shot,
                    metric_text="Fake MRP",
                    status="flagged",
                )
            elif "expired" in body_text.lower():
                await self.blackboard.post_finding(
                    universe=self.universe_id,
                    category="DEADLINE",
                    title="Expired Deadline",
                    details=f"{site_slug} application window is expired.",
                    severity="high",
                    evidence_url=url,
                    site=site_slug,
                )
                await self.emit_dynamic(
                    action=f"[DeadlineExpired] {site_slug} window closed; pruning dead-end.",
                    target_url=url,
                    screenshot_b64=shot,
                    metric_text="Expired",
                    status="flagged",
                )
            else:
                await self.blackboard.post_finding(
                    universe=self.universe_id,
                    category="VERIFIED_CLEAN",
                    title=f"{site_slug} clean terms",
                    details=f"No lock-ins, hidden fees, or disqualifying fine print on {site_slug}.",
                    severity="positive",
                    evidence_url=url,
                    site=site_slug,
                )
                await self.emit_dynamic(
                    action=f"Verified clean terms & eligibility on {site_slug}.",
                    target_url=url,
                    screenshot_b64=shot,
                    metric_text="Verified Clean",
                    status="discovery",
                )
            return

        # 3. LANDED COST / CHECKOUT DRILLDOWN
        if focus == "landed_cost":
            checkout_btn = await page.query_selector("#btn-proceed-checkout")
            if checkout_btn:
                displayed_el = await page.query_selector("#displayed-price")
                listed_val = float((await displayed_el.inner_text()).strip()) if displayed_el else 0.0

                await checkout_btn.click()
                await page.wait_for_load_state("domcontentloaded")
                checkout_url = page.url
                c_shot = await self._snap(page)

                final_el = await page.query_selector("#final-landed-price")
                landed_val = float((await final_el.inner_text()).strip()) if final_el else listed_val

                if landed_val > listed_val:
                    diff = int(landed_val - listed_val)
                    await self.blackboard.post_dark_pattern(
                        universe=self.universe_id,
                        pattern_type="DRIP_PRICING",
                        details=f"[{site_slug}] Checkout injected +₹{diff} in unlisted fees (₹{int(listed_val)} → ₹{int(landed_val)}).",
                        evidence_url=checkout_url,
                        site=site_slug,
                    )
                    await self.emit_dynamic(
                        action=f"[DripPricingDetected] {site_slug} added +₹{diff} at checkout → ₹{int(landed_val)}.",
                        target_url=checkout_url,
                        screenshot_b64=c_shot,
                        found_price=landed_val,
                        metric_text=f"₹{int(landed_val):,}",
                        status="flagged",
                    )

                # Check Blackboard for peer vouchers!
                await asyncio.sleep(0.4)
                coupons = await self.blackboard.get_valid_coupons(site=site_slug)
                if coupons:
                    code = coupons[0]["code"]
                    inp = await page.query_selector("#coupon-input")
                    apply_btn = await page.query_selector("#btn-apply-coupon")
                    if inp and apply_btn:
                        await inp.fill(code)
                        await apply_btn.click()
                        await page.wait_for_load_state("domcontentloaded")
                        c2_shot = await self._snap(page)
                        final_el2 = await page.query_selector("#final-landed-price")
                        new_val = float((await final_el2.inner_text()).strip()) if final_el2 else landed_val
                        await self.emit_dynamic(
                            action=f"[BlackboardSync] Applied peer voucher '{code}' at {site_slug} checkout → ₹{int(new_val)}.",
                            target_url=page.url,
                            screenshot_b64=c2_shot,
                            found_price=new_val,
                            metric_text=f"₹{int(new_val):,}",
                            status="discovery",
                        )
                        self.findings["best_landed"] = {"site": site_slug, "price": new_val, "coupon": code}
                        return

                self.findings.setdefault("prices", []).append({"site": site_slug, "price": landed_val})
            else:
                # Non-checkout portal page (travel, plans, medicines, etc.)
                metric_el = await page.query_selector("#headline-metric")
                metric_txt = (await metric_el.inner_text()).strip() if metric_el else "Audited"
                catch_els = await page.query_selector_all(".catch-box[data-catch-type='DRIP_FEE']")
                if catch_els:
                    txt = re.sub(r"\s+", " ", (await catch_els[0].inner_text()).strip())
                    await self.emit_dynamic(
                        action=f"[CostAudit] {site_slug} advertises {metric_txt}, catch: {txt[:90]}",
                        target_url=url,
                        screenshot_b64=shot,
                        metric_text=f"{metric_txt}+",
                        status="flagged",
                    )
                else:
                    await self.emit_dynamic(
                        action=f"Audited true cost baseline on {site_slug}: {metric_txt}",
                        target_url=url,
                        screenshot_b64=shot,
                        metric_text=metric_txt,
                        status="running",
                    )
            return

        # 4. VALUE MATRIX / ALTERNATIVE MODE
        metric_el = await page.query_selector("#headline-metric, #displayed-price")
        metric_txt = (await metric_el.inner_text()).strip() if metric_el else "Evaluated"
        if "₹" not in metric_txt and metric_txt.replace(".", "").isdigit():
            metric_txt = f"₹{metric_txt}"
        await self.emit_dynamic(
            action=f"[{self.spec.role}] Evaluated {site_slug} ({metric_txt}) against constraints.",
            target_url=url,
            screenshot_b64=shot,
            metric_text=metric_txt,
            status="running",
        )

    def _extract_site_slug(self, url: str) -> str:
        parts = [p for p in urlparse(url).path.split("/") if p]
        if len(parts) >= 2 and parts[0] in ("mock", "portal"):
            return parts[1] if parts[0] == "mock" else parts[-1]
        return parts[-1] if parts else "site"

    async def _run_simulated_fallback(self, urls: List[str]):
        """Fallback path when Playwright browser isn't attached."""
        for url in urls:
            slug = self._extract_site_slug(url)
            await self.emit_dynamic(
                action=f"Inspecting {slug} ({self.spec.role})",
                target_url=url,
                status="running",
            )
            await asyncio.sleep(0.3)
        await self.emit_dynamic(
            action=f"{self.spec.title} completed.",
            metric_text="Done",
            status="completed",
        )
