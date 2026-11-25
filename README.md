# Multiverse Browser
> One goal, many universes, one verdict you can trust.

**wHACKiest 2026** · **Track 2: Beyond the Browser (Reimagine How We Use the Web)**  
*Team CodeRIT · Ramaiah Institute of Technology*

---

## 1. What Multiverse Browser Actually Is

Multiverse Browser is **not just a shopping price checker**. It is a **general-purpose parallel web-goal engine** for any task that forces a person to open 15 tabs, cross-check constraints, and dig through fine print to uncover hidden catches (fees, eligibility cutoffs, deadlines, lock-ins, cancellation traps, or better alternative paths).

Instead of running a single linear browser agent or hardcoding a fixed set of views, a **Dynamic Strategy Planner** inspects your goal, decides **how many parallel universes (`N`) are needed** for that specific problem, assigns each universe a distinct exploration strategy, and spawns `N` isolated Playwright browser workers that share discoveries on a live **Blackboard**.

### Target Use Cases
* **Money & Shopping**
  * *Big purchases* (laptops, phones, headphones): cheapest new checkout, refurbished, student discounts, last-gen alternatives, sale timing.
  * *Plans & bills* (broadband, mobile, insurance, credit cards): base vs post-promo renewal surge, benefits, hidden fees, lock-in clauses.
  * *Medicines*: brand vs Jan Aushadhi generic salt match vs 1mg/Netmeds/local delivery cost & ETA.
* **Travel & Logistics**
  * *Trips*: flights vs train vs bus, split-ticket routes, baggage drip fees, cancellation fine print, promos.
  * *Stays*: hotels, hostels, PGs, or rentals weighting commute, total cost, and safety signals.
* **Student & Career Life**
  * *Opportunities*: scholarships, internships, hackathons, jobs — scoring eligibility against your profile and pruning expired/bonded traps.
  * *Courses*: free or low-cost learning paths comparing YouTube, MOOC audit/financial aid, official docs, and books.

---

## 2. How It Works

![Multiverse Browser System Architecture](docs/architecture.svg)

1. **Goal Ingestion**: Speak (ElevenLabs Scribe STT) or type any web goal.
2. **Dynamic Strategy Planning (`backend/app/planner.py`)**: Analyzes the domain and prompt constraints to dynamically allocate **`N` universes** (e.g., 3 for a focused plan/medicine check, 4–5 for multi-constraint travel, scholarships, or big purchases).
3. **Parallel Playwright Swarm (`backend/app/universes/dynamic_worker.py`)**: Spawns `N` isolated headless Chromium browser contexts under strict read-only guardrails, navigating candidate sites and capturing live screenshot receipts.
4. **Shared Blackboard (`backend/app/blackboard.py`)**: Universes publish vouchers, drip-pricing traps, expired deadlines, bond clauses, or generic equivalents mid-flight so peer universes adapt live.
5. **Multiverse Judge (`backend/app/integrations/aws_client.py`)**: Synthesizes evidence across whichever `N` universes ran into one reconciled verdict with proof and spoken audio (ElevenLabs TTS).

---

## 3. Honesty & Transparency Matrix

| Component | Status | Technical Reality |
|---|---|---|
| **Dynamic Strategy Planner (`N` Universes)** | 🟢 **Real** | Analyzes goal domain & constraint facets to dynamically allocate 2–6 tailored universes; optional Bedrock LLM planner hook included. |
| **Swarm Orchestrator & Shared Blackboard** | 🟢 **Real** | Asyncio parallel runner with live WebSockets (`/ws/stream`) and cross-agent pub/sub discovery exchange. |
| **Playwright Headless Browser Execution** | 🟢 **Real** | Spawns isolated Chromium contexts, clicks through checkout/terms pages, applies blackboard vouchers in real DOM inputs, and streams live JPEG screenshots. |
| **Multi-Domain Self-Hosted Testbed** | 🟢 **Real / Mocked** | Self-hosted portals across e-commerce (`/mock/*`), travel, scholarships, plans/bills, medicines, and courses (`/portal/*`) with planted fine-print catches. |
| **Dynamic Swarm Control UI** | 🟢 **Real** | Live light-theme WebSocket dashboard that dynamically renders `N` browser tiles based on the planner output. |
| **ElevenLabs Voice (STT & TTS)** | 🟠 **Stubbed Interface** | Client wrappers (`transcribe_speech`, `generate_verdict_audio`) ready for API key injection; falls back cleanly to Web Speech API in browser. |
| **AWS Bedrock Judge & S3 Storage** | 🟠 **Stubbed Interface** | Domain-aware deterministic judge reconciliation + S3 URL generator; falls back cleanly without requiring AWS credentials. |
| **Live Anti-Bot Commercial Sites** | 🔵 **Planned (Post-Hackathon)** | Chrome extension running universes in the user's own authenticated browser session to bypass Cloudflare/Akamai bot walls. |

---

## 4. Real-World Limits & Engineering Trade-offs

1. **Why Self-Hosted Multi-Domain Portals for the Demo?**  
   Commercial sites (Amazon, MakeMyTrip, Coursera, airlines) enforce Cloudflare/Akamai bot walls against datacenter headless browsers. Self-hosted portals across 6 domains let us demonstrate real Playwright multi-universe execution, DOM interaction, screenshot capture, and planted fine-print traps reliably in a 5-minute live pitch.
2. **Dynamic `N` Sizing & Cost Control**  
   Running 8 universes on a simple question wastes latency and tokens. The Strategy Planner scales `N` dynamically to the goal's complexity, and keeps worker budgets capped (`15` steps / `60s` max).
3. **Swarm Resilience**  
   On the open web, single browser agents fail ~20–40% of the time on layout changes or dead links. Because universes race in parallel and dead-ends are pruned, the Judge still produces a receipt-backed verdict from surviving universes.

---

## 5. Telemetry & Safety Guardrails

* **Read-Only Mode**: Agents never submit passwords, OTPs, or payment details.
* **Domain Allowlist**: Navigation outside allowed domains is blocked (`_is_allowed_url`).
* **Step & Time Caps**: Max 15 steps and 60s timeout per universe.
* **Human-in-the-Loop**: Final action/checkout always stays with the user.

---

## 6. Quickstart & Local Reproduction

```bash
# Clone the repository
git clone https://github.com/KartikRL1201/Multiverse-Browser.git
cd Multiverse-Browser

# Set up virtual environment and install dependencies
uv venv .venv
source .venv/bin/activate
uv pip install -r backend/requirements.txt

# Run the FastAPI server + Playwright swarm engine
.venv/bin/uvicorn backend.app.main:app --port 8000
```

1. Open **`http://localhost:8000/`**.
2. Pick any preset domain goal (Shopping, Travel, Scholarships, Plans & Bills, Medicines, Courses) or enter your own custom web goal.
3. Click **PLAN & EXECUTE SWARM** and watch the Planner dynamically spawn `N` isolated Playwright browsers, exchange discoveries on the Shared Blackboard, and stream live screenshots to the verdict card.
4. Inspect the raw self-hosted portals at **`http://localhost:8000/portal`** and **`http://localhost:8000/mock`**.
