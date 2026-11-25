import os
import json
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class UniverseSpec(BaseModel):
    universe_id: str
    title: str
    role: str
    strategy: str
    focus_type: str  # landed_cost | voucher_hunt | fine_print | eligibility | value_matrix | alternative_mode
    metric_label: str
    target_urls: List[str]


class SwarmPlan(BaseModel):
    goal: str
    domain: str
    universe_count: int
    reasoning: str
    target_urls: List[str]
    universes: List[UniverseSpec]


class StrategyPlanner:
    """
    Dynamically analyzes any user web goal and determines:
    1. The task domain (shopping, travel, stays, plans, medicines, opportunities, courses, or general).
    2. How many parallel universes (N) are actually needed based on constraints and trade-offs.
    3. Distinct, non-overlapping exploration heuristics for each of the N universes.
    """

    def __init__(self, base_url: Optional[str] = None):
        resolved = base_url or os.getenv("APP_BASE_URL", "http://127.0.0.1:8000")
        self.base_url = resolved.rstrip("/")

    def _detect_domain(self, goal_lower: str) -> str:
        if any(k in goal_lower for k in ["medicine", "tablet", "paracetamol", "pharmacy", "generic", "jan aushadhi", "1mg", "netmeds", "meds"]):
            return "medicines"
        if any(k in goal_lower for k in ["scholarship", "fellowship", "grant", "internship", "hackathon", "eligibility", "b.tech", "student aid"]):
            return "opportunities"
        if any(k in goal_lower for k in ["flight", "train", "bus", "trip", "travel", "blr", "del", "ticket", "airport", "baggage", "route"]):
            return "travel"
        if any(k in goal_lower for k in ["hotel", "hostel", "pg ", "rental", "stay", "commute", "room"]):
            return "stays"
        if any(k in goal_lower for k in ["broadband", "fiber", "plan", "recharge", "insurance", "credit card", "subscription", "cloudvault", "saas", "bill"]):
            return "plans_bills"
        if any(k in goal_lower for k in ["course", "learn", "rust", "python", "mooc", "coursera", "youtube", "bootcamp", "tutorial"]):
            return "courses"
        if any(k in goal_lower for k in ["headphone", "laptop", "phone", "buy", "shop", "under ₹", "under rs", "price", "refurbished", "product", "earbud"]):
            return "shopping"
        return "general"

    def _default_urls_for_domain(self, domain: str) -> List[str]:
        if domain == "shopping":
            return [
                f"{self.base_url}/mock/electrobazaar/soundpulse-500",
                f"{self.base_url}/mock/dealnest/soundpulse-500",
                f"{self.base_url}/mock/flashkart/soundpulse-500",
            ]
        if domain in ("travel", "stays"):
            return [
                f"{self.base_url}/portal/travel/skyfare",
                f"{self.base_url}/portal/travel/airhopper",
                f"{self.base_url}/portal/travel/railyatra",
            ]
        if domain == "opportunities":
            return [
                f"{self.base_url}/portal/scholarship/meritgrant",
                f"{self.base_url}/portal/scholarship/techfuture",
                f"{self.base_url}/portal/scholarship/statefund",
            ]
        if domain == "plans_bills":
            return [
                f"{self.base_url}/portal/plans/cloudvault",
                f"{self.base_url}/portal/plans/openfiber",
            ]
        if domain == "medicines":
            return [
                f"{self.base_url}/portal/medicines/brandpharma",
                f"{self.base_url}/portal/medicines/janaushadhi",
                f"{self.base_url}/portal/medicines/netpharmacy",
            ]
        if domain == "courses":
            return [
                f"{self.base_url}/portal/courses/bootcamp",
                f"{self.base_url}/portal/courses/mooc_audit",
                f"{self.base_url}/portal/courses/docs_yt",
            ]
        # General fallback mixes portals to audit options + fine print
        return [
            f"{self.base_url}/portal/plans/cloudvault",
            f"{self.base_url}/portal/plans/openfiber",
            f"{self.base_url}/mock/dealnest/soundpulse-500",
        ]

    async def create_plan(self, goal: str, target_urls: Optional[List[str]] = None) -> SwarmPlan:
        goal_clean = goal.strip() or "Find the best option without hidden catches"
        goal_lower = goal_clean.lower()

        # Optional AWS Bedrock dynamic planning if credentials are configured
        if os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("ENABLE_BEDROCK_PLANNER") == "1":
            bedrock_plan = await self._try_bedrock_plan(goal_clean, target_urls)
            if bedrock_plan:
                return bedrock_plan

        domain = self._detect_domain(goal_lower)
        urls = target_urls if target_urls else self._default_urls_for_domain(domain)

        # Dynamically choose N universes based on domain & prompt facets
        universes: List[UniverseSpec] = []

        if domain == "shopping":
            universes.append(UniverseSpec(
                universe_id="u_landed_cost",
                title="Landed Cost Auditor",
                role="Checkout & Drip-Fee Verification",
                strategy="Drills down to final checkout to uncover hidden handling/packaging fees and compute true cost.",
                focus_type="landed_cost",
                metric_label="True Checkout",
                target_urls=urls,
            ))
            universes.append(UniverseSpec(
                universe_id="u_vouchers",
                title="Promo & Student Deal Scraper",
                role="Coupon & Discount Extraction",
                strategy="Scans promotional banners, footers, and student perks; publishes valid codes to the blackboard.",
                focus_type="voucher_hunt",
                metric_label="Voucher Found",
                target_urls=urls,
            ))
            universes.append(UniverseSpec(
                universe_id="u_trust",
                title="Trust & Fake-MRP Auditor",
                role="Authenticity & Warranty Verification",
                strategy="Cross-checks seller warranty terms and flags inflated anchor MRPs.",
                focus_type="fine_print",
                metric_label="Trust Audit",
                target_urls=urls,
            ))
            # Dynamically spawn extra universes if goal mentions specs/value, refurbished, or sale timing
            if any(k in goal_lower for k in ["anc", "best", "value", "battery", "quality", "feature", "rating", "compare", "refurb", "last-gen", "sale"]):
                universes.append(UniverseSpec(
                    universe_id="u_value",
                    title="Spec / Feature Matrix",
                    role="Utility & Trade-off Scoring",
                    strategy="Evaluates battery, specs, and review signals relative to net landed cost.",
                    focus_type="value_matrix",
                    metric_label="Value Score",
                    target_urls=urls,
                ))
            if any(k in goal_lower for k in ["refurbished", "last-gen", "student", "sale", "wait"]):
                universes.append(UniverseSpec(
                    universe_id="u_alt_path",
                    title="Refurb & Last-Gen Scout",
                    role="Alternative Acquisition Paths",
                    strategy="Evaluates certified refurbished, prior-generation models, and upcoming sale drops.",
                    focus_type="alternative_mode",
                    metric_label="Alt Savings",
                    target_urls=urls,
                ))
            reasoning = (
                f"Detected e-commerce goal with {len(universes)} verification axes "
                f"(checkout drip fees, hidden vouchers, MRP/warranty trust"
                f"{', specs/value' if len(universes) >= 4 else ''}"
                f"{', alternative/refurb paths' if len(universes) >= 5 else ''})."
            )

        elif domain == "travel":
            universes.append(UniverseSpec(
                universe_id="u_fare_audit",
                title="Baggage & Drip-Fee Auditor",
                role="True Door-to-Door Fare",
                strategy="Follows flight checkout to uncover 15kg baggage fees and gateway surcharges.",
                focus_type="landed_cost",
                metric_label="True Fare",
                target_urls=urls,
            ))
            universes.append(UniverseSpec(
                universe_id="u_ground_alt",
                title="Train / Bus / Split-Route Scout",
                role="Multimodal Route Comparison",
                strategy="Races overnight rail/bus and split-ticket alternatives against direct flights.",
                focus_type="alternative_mode",
                metric_label="Alt Route",
                target_urls=urls,
            ))
            universes.append(UniverseSpec(
                universe_id="u_cancel_rules",
                title="Cancellation & Fine-Print Reader",
                role="Fare Rules & Flexibility Audit",
                strategy="Reads fine-print clauses to flag zero-refund lock-in and reschedule penalties.",
                focus_type="fine_print",
                metric_label="Flex Check",
                target_urls=urls,
            ))
            universes.append(UniverseSpec(
                universe_id="u_travel_promo",
                title="Airline & Card Promo Hunter",
                role="Banner & Bank Code Scraper",
                strategy="Extracts airline voucher codes and broadcasts savings to peer route universes.",
                focus_type="voucher_hunt",
                metric_label="Promo Offset",
                target_urls=urls,
            ))
            if any(k in goal_lower for k in ["flexible", "date", "nearby", "layover", "direct", "fastest"]):
                universes.append(UniverseSpec(
                    universe_id="u_transit_time",
                    title="Transit & Layover Viability",
                    role="Time-vs-Money Optimizer",
                    strategy="Flags painful overnight layovers, waitlist risk, and terminal transfers.",
                    focus_type="value_matrix",
                    metric_label="Transit Risk",
                    target_urls=urls,
                ))
            reasoning = f"Travel intent spans multiple transport modes and hidden airline fees; dynamically spawning {len(universes)} parallel universes."

        elif domain == "opportunities":
            universes.append(UniverseSpec(
                universe_id="u_eligibility",
                title="Eligibility & Profile Matcher",
                role="Year / Income / Criteria Audit",
                strategy="Checks year of study, GPA, and income caps against user profile constraints.",
                focus_type="eligibility",
                metric_label="Eligibility",
                target_urls=urls,
            ))
            universes.append(UniverseSpec(
                universe_id="u_deadlines",
                title="Deadline & Portal Status Verifier",
                role="Active Window Verification",
                strategy="Checks footer dates to drop expired opportunities before wasting application effort.",
                focus_type="fine_print",
                metric_label="Deadline",
                target_urls=urls,
            ))
            universes.append(UniverseSpec(
                universe_id="u_bond_traps",
                title="Fine-Print & Bond Trap Reader",
                role="Clause & Lock-in Inspection",
                strategy="Scans terms for post-graduation service bonds or hidden clawback conditions.",
                focus_type="fine_print",
                metric_label="Clause Risk",
                target_urls=urls,
            ))
            universes.append(UniverseSpec(
                universe_id="u_perks",
                title="Stackable Stipend & Bonus Hunter",
                role="Net Financial Value",
                strategy="Finds footnote book/hardware stipends and broadcasts stackable codes to the blackboard.",
                focus_type="voucher_hunt",
                metric_label="Net Grant",
                target_urls=urls,
            ))
            reasoning = f"Opportunity search requires verifying eligibility, live deadlines, bond clauses, and stackable grants across {len(universes)} universes."

        elif domain == "plans_bills":
            universes.append(UniverseSpec(
                universe_id="u_renewal",
                title="Intro vs Renewal Cost Auditor",
                role="12-Month Effective Rate",
                strategy="Computes true annualized monthly cost after promo periods expire.",
                focus_type="landed_cost",
                metric_label="Effective/mo",
                target_urls=urls,
            ))
            universes.append(UniverseSpec(
                universe_id="u_lockin",
                title="Lock-In & Cancellation Reader",
                role="Contract Trap Detection",
                strategy="Audits fine print for early termination penalties, router leases, and notice windows.",
                focus_type="fine_print",
                metric_label="Trap Audit",
                target_urls=urls,
            ))
            universes.append(UniverseSpec(
                universe_id="u_plan_perks",
                title="Student / Autopay Discount Hunter",
                role="Unlisted Tier Discounts",
                strategy="Checks footer verification links for student/campus promo codes.",
                focus_type="voucher_hunt",
                metric_label="Tier Discount",
                target_urls=urls,
            ))
            reasoning = f"Plan & bill comparison focuses on post-promo renewal spikes, contract lock-ins, and tier discounts ({len(universes)} universes)."

        elif domain == "medicines":
            universes.append(UniverseSpec(
                universe_id="u_generic",
                title="Generic & Jan Aushadhi Matcher",
                role="Active Salt Equivalence",
                strategy="Matches exact chemical salt composition against low-cost generic / PMBJP alternatives.",
                focus_type="alternative_mode",
                metric_label="Generic Cost",
                target_urls=urls,
            ))
            universes.append(UniverseSpec(
                universe_id="u_delivery",
                title="Pharmacy Delivery & Cart Fee Auditor",
                role="Doorstep Landed Cost",
                strategy="Compares 1mg/Netmeds/local delivery fees and small-cart surcharges.",
                focus_type="landed_cost",
                metric_label="Delivered",
                target_urls=urls,
            ))
            universes.append(UniverseSpec(
                universe_id="u_med_promo",
                title="First-Order & Generic Coupon Scout",
                role="Pharmacy Promo Extraction",
                strategy="Finds app promo codes for generic orders and shares them on the blackboard.",
                focus_type="voucher_hunt",
                metric_label="Promo",
                target_urls=urls,
            ))
            reasoning = f"Medicine comparison decomposes into chemical salt equivalence, delivery landed cost, and promo lookup ({len(universes)} universes)."

        elif domain == "courses":
            universes.append(UniverseSpec(
                universe_id="u_open_path",
                title="Free Docs & OCW Path",
                role="Zero-Cost Open Curriculum",
                strategy="Evaluates official docs, MIT OCW, and community project tracks with zero paywalls.",
                focus_type="alternative_mode",
                metric_label="Open Cost",
                target_urls=urls,
            ))
            universes.append(UniverseSpec(
                universe_id="u_mooc_aid",
                title="MOOC Audit & Financial Aid Scout",
                role="Hidden Free-Access Links",
                strategy="Detects paywalled graded labs and surfaces buried Financial Aid application links.",
                focus_type="voucher_hunt",
                metric_label="Aid Path",
                target_urls=urls,
            ))
            universes.append(UniverseSpec(
                universe_id="u_bootcamp_audit",
                title="Paid Bootcamp & EMI Catch Auditor",
                role="Syllabus Freshness & Fee Check",
                strategy="Flags outdated curricula and hidden EMI processing fees on commercial bootcamps.",
                focus_type="fine_print",
                metric_label="Catch Check",
                target_urls=urls,
            ))
            reasoning = f"Learning path evaluation spawns {len(universes)} universes: open/free tracks, MOOC financial aid, and paid bootcamp catch auditing."

        else:
            # General dynamic decomposition based on prompt tokens/conjunctions
            clauses = [c.strip() for c in goal_clean.replace(" and ", ",").replace(" with ", ",").split(",") if c.strip()]
            n_dynamic = min(max(len(clauses) + 1, 2), 5)
            templates = [
                ("u_primary", "Primary Option Explorer", "Baseline Discovery", "Surfaces primary candidates and advertised claims.", "landed_cost", "Headline"),
                ("u_catches", "Fine-Print & Risk Auditor", "Catch & Trap Detection", "Scans terms, fees, lock-ins, and hidden exclusions.", "fine_print", "Catches"),
                ("u_perks", "Perks & Shortcut Hunter", "Hidden Value Extraction", "Finds unlisted codes, waivers, or free tiers and posts to blackboard.", "voucher_hunt", "Savings"),
                ("u_alternatives", "Alternative Path Scout", "Non-Obvious Options", "Explores adjacent/generic/open alternatives outside standard listings.", "alternative_mode", "Alt Path"),
                ("u_synthesis", "Constraint Verifier", "Profile & Fit Scoring", "Verifies all user constraints against collected evidence.", "value_matrix", "Fit Score"),
            ]
            for i in range(n_dynamic):
                tid, title, role, strat, ftype, mlabel = templates[i]
                universes.append(UniverseSpec(
                    universe_id=tid,
                    title=title,
                    role=role,
                    strategy=strat,
                    focus_type=ftype,
                    metric_label=mlabel,
                    target_urls=urls,
                ))
            reasoning = f"General web goal analyzed ({len(clauses)} constraint group(s)); dynamically allocated {len(universes)} parallel universes."

        return SwarmPlan(
            goal=goal_clean,
            domain=domain,
            universe_count=len(universes),
            reasoning=reasoning,
            target_urls=urls,
            universes=universes,
        )

    async def _try_bedrock_plan(self, goal: str, target_urls: Optional[List[str]]) -> Optional[SwarmPlan]:
        """Placeholder hook for live AWS Bedrock Claude dynamic planning."""
        try:
            # Future: invoke boto3 bedrock-runtime to return dynamic JSON SwarmPlan
            return None
        except Exception as exc:
            logger.warning(f"Bedrock planner fallback triggered: {exc}")
            return None
