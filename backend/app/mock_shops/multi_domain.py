from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/portal", tags=["Multi-Domain Mock Web Portals"])

PORTAL_DATA = {
    "travel": {
        "title": "Travel & Route Options (BLR → DEL)",
        "items": {
            "skyfare": {
                "name": "SkyFare Basic Economy (BLR → DEL)",
                "provider": "SkyFare Airlines",
                "headline_metric": "₹4,299",
                "base_cost": 4299,
                "true_cost": 5848,
                "route_type": "Flight (Direct, 2h 45m)",
                "badge": "Lowest Advertised",
                "catches": [
                    {"type": "DRIP_FEE", "title": "Mandatory Check-in Baggage (+₹1,150)", "details": "Zero check-in luggage included on Basic tier; 15kg bag adds ₹1,150 at step 2."},
                    {"type": "DRIP_FEE", "title": "Convenience Fee (+₹399)", "details": "Non-waivable payment gateway fee injected on final payment screen."},
                    {"type": "FINE_PRINT", "title": "Zero-Refund Lock-In", "details": "Fine print clause 4.2: 100% forfeiture on cancellation or date change."}
                ],
                "coupon": None,
                "checkout_notes": "Total moves from ₹4,299 advertised to ₹5,848 with 15kg baggage."
            },
            "airhopper": {
                "name": "AirHopper Flex + Split-Airport Option (BLR → DEL)",
                "provider": "AirHopper",
                "headline_metric": "₹4,750",
                "base_cost": 4750,
                "true_cost": 4250,
                "route_type": "Flight (15kg Bag + Free Reschedule)",
                "badge": "Verified Flexible",
                "catches": [],
                "coupon": {"code": "FLY500", "discount": 500, "location": "Partner bank banner in footer"},
                "checkout_notes": "Includes 15kg baggage and free 24h reschedule. Drops to ₹4,250 with FLY500."
            },
            "railyatra": {
                "name": "Rajdhani / Overnight 2AC Train + Bus Combo",
                "provider": "RailYatra",
                "headline_metric": "₹2,890",
                "base_cost": 2890,
                "true_cost": 2890,
                "route_type": "Overnight Train (33h)",
                "badge": "Lowest Cost Ground",
                "catches": [
                    {"type": "FINE_PRINT", "title": "33-Hour Transit Duration", "details": "Saves ₹1,360 vs best flight, but arrives next evening (WL#4 confirmation risk)."}
                ],
                "coupon": None,
                "checkout_notes": "Flat ₹2,890 including meals; zero hidden fees, high transit time."
            }
        }
    },
    "scholarship": {
        "title": "Scholarships & Student Grants Portal",
        "items": {
            "meritgrant": {
                "name": "National STEM Excellence Award",
                "provider": "MeritGrant Foundation",
                "headline_metric": "₹1,00,000",
                "net_benefit": 0,
                "eligible": False,
                "deadline": "15 Nov (EXPIRED)",
                "catches": [
                    {"type": "DEADLINE", "title": "Application Window Closed", "details": "Portal footer note: Submissions closed 15 Nov; page still indexed in search."},
                    {"type": "ELIGIBILITY", "title": "1st-Year Only + 2-Year Service Bond", "details": "Fine print section 7: Restricted to incoming 1st-year students and requires a 2-year work bond."}
                ],
                "perk": None
            },
            "techfuture": {
                "name": "TechFuture Undergraduate Fellowship",
                "provider": "TechFuture Org",
                "headline_metric": "₹60,000",
                "net_benefit": 75000,
                "eligible": True,
                "deadline": "10 Dec (Open)",
                "catches": [],
                "perk": {"code": "TECHBOOKS", "value": 15000, "details": "Footnote: Stackable ₹15,000 hardware/book stipend with code TECHBOOKS."}
            },
            "statefund": {
                "name": "State Tuition Relief Scheme",
                "provider": "State Higher Ed Portal",
                "headline_metric": "₹50,000",
                "net_benefit": 50000,
                "eligible": True,
                "deadline": "30 Nov (Closing Soon)",
                "catches": [
                    {"type": "ELIGIBILITY", "title": "Income Cap ≤ ₹6,00,000 & Bonafide Required", "details": "Requires signed college bonafide certificate uploaded 48h before deadline."}
                ],
                "perk": None
            }
        }
    },
    "plans": {
        "title": "Broadband, Mobile & SaaS Plans",
        "items": {
            "cloudvault": {
                "name": "CloudVault Pro 1Gbps / Suite",
                "provider": "CloudVault",
                "headline_metric": "₹199/mo",
                "base_cost": 199,
                "true_monthly_avg": 874,
                "catches": [
                    {"type": "FINE_PRINT", "title": "350% Post-Promo Renewal Surge", "details": "Clause 3.1: ₹199 applies to Month 1 only; auto-renews at ₹899/mo for remaining 11 months."},
                    {"type": "DRIP_FEE", "title": "Mandatory Router Rental (+₹99/mo)", "details": "Hardware lease fee added on billing summary."},
                    {"type": "FINE_PRINT", "title": "12-Month Lock-in & 30-Day Written Notice", "details": "Early termination incurs ₹2,500 penalty."}
                ],
                "coupon": None
            },
            "openfiber": {
                "name": "OpenFiber Transparent 300Mbps",
                "provider": "OpenFiber",
                "headline_metric": "₹499/mo",
                "base_cost": 499,
                "true_monthly_avg": 349,
                "catches": [],
                "coupon": {"code": "EDU30", "discount": 150, "location": "Student / campus verification footer (-30%)"}
            }
        }
    },
    "medicines": {
        "title": "Pharmacy & Generic Salt Comparison",
        "items": {
            "brandpharma": {
                "name": "BrandName Pain & Fever Relief (15 Tabs)",
                "provider": "QuickMed App",
                "headline_metric": "₹185",
                "base_cost": 185,
                "true_cost": 225,
                "salt": "Paracetamol 650mg + Caffeine",
                "catches": [
                    {"type": "DRIP_FEE", "title": "Small Cart Handling Fee (+₹40)", "details": "Delivery + platform fee added below ₹299."}
                ],
                "coupon": None
            },
            "janaushadhi": {
                "name": "Jan Aushadhi Generic Equivalent (15 Tabs)",
                "provider": "PMBJP Store Locator / Generic",
                "headline_metric": "₹18",
                "base_cost": 18,
                "true_cost": 18,
                "salt": "Paracetamol 650mg (Exact Active Salt Match)",
                "catches": [
                    {"type": "FINE_PRINT", "title": "In-Store Pickup Required (1.2 km)", "details": "No instant 10-min app delivery; verified identical active salt at 92% lower cost."}
                ],
                "coupon": None
            },
            "netpharmacy": {
                "name": "Generic Equivalent Delivered (1mg / Netmeds)",
                "provider": "1mg Generic",
                "headline_metric": "₹42",
                "base_cost": 42,
                "true_cost": 35,
                "salt": "Paracetamol 650mg",
                "catches": [],
                "coupon": {"code": "FIRST15", "discount": 7, "location": "App banner 15% off generic orders"}
            }
        }
    },
    "courses": {
        "title": "Learning Paths & Course Comparison",
        "items": {
            "bootcamp": {
                "name": "Pro Full-Stack & Systems Bootcamp",
                "provider": "CodeSprint Academy",
                "headline_metric": "₹24,999",
                "true_cost": 24999,
                "catches": [
                    {"type": "FINE_PRINT", "title": "Outdated 2022 Curriculum & EMI Interest", "details": "Reviews cite pre-recorded 2022 videos; 'No-cost EMI' adds 14% processing fee."}
                ],
                "coupon": None
            },
            "mooc_audit": {
                "name": "University Systems Specialization (Audit Mode)",
                "provider": "Coursera / edX",
                "headline_metric": "₹0 (Audit)",
                "true_cost": 0,
                "catches": [
                    {"type": "FINE_PRINT", "title": "Graded Labs Paywalled (₹4,100/mo)", "details": "Free audit hides coding assignments unless Financial Aid is clicked in tiny link."}
                ],
                "coupon": {"code": "FIN_AID_LINK", "discount": 4100, "location": "Small 'Financial aid available' link under Enroll"}
            },
            "docs_yt": {
                "name": "Official Docs + MIT OCW + Community Projects",
                "provider": "Open Web Curriculum",
                "headline_metric": "₹0 (Free)",
                "true_cost": 0,
                "catches": [],
                "coupon": None
            }
        }
    }
}


@router.get("/", response_class=HTMLResponse)
async def portal_hub():
    cards = ""
    for domain, ddata in PORTAL_DATA.items():
        links = "".join(
            f'<li><a href="/portal/{domain}/{item_id}">{item["name"]} ({item["headline_metric"]})</a></li>'
            for item_id, item in ddata["items"].items()
        )
        cards += f"""
        <div class="card">
            <h2>{ddata['title']} <code>/portal/{domain}</code></h2>
            <ul>{links}</ul>
        </div>
        """
    return HTMLResponse(f"""<!DOCTYPE html>
    <html><head><title>Multiverse Browser · Multi-Domain Testbed</title>
    <style>
        body {{ font-family: system-ui, sans-serif; max-width: 860px; margin: 40px auto; background: #f8fafc; color: #0f172a; padding: 0 20px; }}
        .card {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 18px; margin-bottom: 16px; }}
        a {{ color: #2563eb; text-decoration: none; font-weight: 600; }}
        code {{ background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-size: 12px; }}
    </style></head>
    <body>
        <h1>Multiverse Browser · Multi-Domain Web Testbed</h1>
        <p>Self-hosted portals across travel, scholarships, plans/bills, medicines, and courses with planted fine-print catches.</p>
        {cards}
        <p><a href="/mock">View E-Commerce Mock Shops →</a> | <a href="/">Back to Swarm Dashboard →</a></p>
    </body></html>""")


@router.get("/{domain}/{item_id}", response_class=HTMLResponse)
async def portal_item(domain: str, item_id: str):
    if domain not in PORTAL_DATA or item_id not in PORTAL_DATA[domain]["items"]:
        raise HTTPException(status_code=404, detail="Portal page not found")

    item = PORTAL_DATA[domain]["items"][item_id]
    catches_html = ""
    for c in item.get("catches", []):
        catches_html += f"""
        <div class="catch-box" data-catch-type="{c['type']}">
            <strong>[{c['type']}] {c['title']}</strong>
            <p>{c['details']}</p>
        </div>
        """

    coupon_html = ""
    if item.get("coupon"):
        cp = item["coupon"]
        coupon_html = f"""
        <div id="promo-banner" data-coupon="{cp['code']}" style="margin-top:20px; background:#fffbeb; border:1px solid #fde68a; padding:12px; border-radius:8px;">
            Hidden Perk ({cp['location']}): <strong id="coupon-code">{cp['code']}</strong> (-{cp['discount']})
        </div>
        """
    if item.get("perk"):
        pk = item["perk"]
        coupon_html = f"""
        <div id="promo-banner" data-coupon="{pk['code']}" style="margin-top:20px; background:#ecfdf5; border:1px solid #a7f3d0; padding:12px; border-radius:8px;">
            Footnote Bonus: <strong id="coupon-code">{pk['code']}</strong> — {pk['details']}
        </div>
        """

    fine_print_note = item.get("checkout_notes") or (
        f"Deadline: {item['deadline']} | Eligible: {item['eligible']}" if "deadline" in item else ""
    )

    return HTMLResponse(f"""<!DOCTYPE html>
    <html><head><title>{item['name']} · {item['provider']}</title>
    <style>
        body {{ font-family: system-ui, sans-serif; background: #f8fafc; color: #0f172a; padding: 30px; }}
        .box {{ max-width: 760px; margin: 0 auto; background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 28px; }}
        .metric {{ font-size: 28px; font-weight: 800; color: #0f172a; margin: 8px 0; }}
        .catch-box {{ margin-top: 12px; padding: 10px 14px; background: #fff1f2; border-left: 4px solid #e11d48; border-radius: 6px; font-size: 13px; }}
        .fine-print {{ margin-top: 24px; font-size: 12px; color: #64748b; border-top: 1px solid #e2e8f0; padding-top: 14px; }}
    </style></head>
    <body>
        <div class="box">
            <div style="font-size:12px; color:#64748b; text-transform:uppercase; font-weight:700;">{item['provider']} · {domain}</div>
            <h1 id="portal-title">{item['name']}</h1>
            <div class="metric" id="headline-metric">{item['headline_metric']}</div>
            <p style="color:#475569;">{fine_print_note}</p>
            {coupon_html}
            <div class="fine-print">
                <div><strong>Terms &amp; Fine Print Audit Section</strong></div>
                {catches_html or '<p style="color:#059669;">No hidden traps or lock-in clauses detected in terms.</p>'}
            </div>
        </div>
    </body></html>""")
