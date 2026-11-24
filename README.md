# 🌌 Multiverse Browser
> **One goal, many universes, one verdict you can trust.**

**wHACKiest 2026** · **Track 2: Beyond the Browser: Reimagine How We Use the Web**  
*Submitted by Team CodeRIT / Ramaiah Institute of Technology*

---

## 📌 Executive Summary

Modern web shopping and online decision-making are plagued by deceptive design patterns: **drip pricing** that injects hidden convenience and handling fees at checkout, **fake MRPs** fabricated to display artificial 60%+ discounts, and fragmented comparison sites that only index deceptive surface listings.

**Multiverse Browser** reimagines browser interaction by deploying a parallel swarm of isolated browser agents ("universes") from a single user intent. Rather than opening 15 tabs or relying on a single linear agent, each universe races with a distinct heuristic:
1. **Budget Universe**: Drills through product listings down to the final checkout step to compute true landed cost (base + shipping + fees - discounts).
2. **Deal Hunter Universe**: Scours promotional banners, markdown footers, and vouchers.
3. **Trust & Signals Universe**: Audits manufacturer warranties, seller ratings, and flags fake MRP inflation.
4. **Best Value Universe**: Optimizes feature-to-price ratios (e.g., ANC, battery life, customer sentiment).

Crucially, the agents communicate via a real-time **Shared Blackboard**. When the Deal Hunter discovers a secret voucher code, other universes immediately inherit that intelligence ("agent telepathy") to recalculate true landed prices. A central **Judge** synthesizes screenshot receipts and delivers a single transparent verdict with proof.

---

## 🏛️ System Architecture

![Multiverse Browser Architecture](docs/architecture.svg)

### Data & Execution Flow
1. **Intent Capture**: User speaks or types a goal (e.g., *"Wireless ANC headphones under ₹3,000"*).
2. **Voice Transcription**: **ElevenLabs Scribe v2** provides sub-150ms speech-to-text with support for Indian regional languages.
3. **Strategy Planning**: An LLM planner (Amazon Bedrock / Claude 3.5) decomposes the goal into 4 specialized universe heuristics.
4. **Parallel Browser Swarm**: Isolated browser sessions (Playwright / AWS AgentCore Browser) navigate candidate stores concurrently under strict read-only guardrails.
5. **Shared Blackboard**: Agents broadcast and consume shared discoveries (valid coupons, hidden fee alerts, fake MRPs, dead ends) in real-time.
6. **AWS S3 Receipt Store**: Automated captures of DOM snapshots and timestamped screenshot receipts.
7. **Verdict & Telemetry**: The Multiverse Judge computes net savings vs naive surface search results, streams live updates via WebSockets to a React board, and provides a spoken regional explanation via **ElevenLabs TTS**.

---

## 🚦 Implementation Status Matrix

In full adherence to the hackathon transparency guidelines:

| Component | Status | Description |
|---|---|---|
| **Swarm Orchestrator & Blackboard** | 🟢 **Real** | Concurrent asyncio worker loop, live blackboard publish/subscribe, and dynamic event streaming. |
| **Planted Mock Ecommerce Testbed** | 🟢 **Real** | 3 self-hosted stores with planted quirks (drip fees, hidden coupons, fake MRPs) for deterministic evaluation. |
| **Interactive Swarm Dashboard** | 🟢 **Real** | Embedded live WebSocket dashboard with live universe tiles, telepathy feed, and verdict card. |
| **Agent Navigation Engine** | 🟡 **Mocked / Scripted PoC** | Deterministic browser execution over self-hosted endpoints with Playwright compatibility hooks. |
| **ElevenLabs Voice (STT & TTS)** | 🟠 **Stubbed Interface** | Functional client interface (`speech_to_text`, `generate_verdict_audio`) ready for API key injection; includes fallback audio generation. |
| **AWS Bedrock Judge & S3 Storage** | 🟠 **Stubbed Interface** | Bedrock judge synthesis pipeline and S3 receipt URL generator; uses local fallback when AWS keys are omitted. |
| **Live Real-World E-Commerce Extension** | 🔵 **Planned (Post-Hackathon)** | Client-side Chrome extension executing browser universes on the user's local session to bypass bot detection. |

---

## 🛰️ Real-Time Telemetry & Event Schema

Every action executed by an agent is streamed via WebSocket (`/ws/stream`) using a structured JSON schema:

```json
{
  "universe": "budget",
  "universe_name": "Budget Universe",
  "step": 3,
  "action": "🚨 DARK PATTERN DETECTED: Drip pricing added +₹348 in fees at checkout! Real price: ₹2547",
  "target_url": "http://localhost:8000/mock/electrobazaar/soundpulse-500/checkout",
  "screenshot": "data:image/png;base64,...",
  "found_price": 2547,
  "status": "flagged",
  "metadata": {
    "drip_fees": 348,
    "original_listed": 2199
  }
}
```

---

## 🛡️ Safety & Guardrails

To prevent unintended transactions or policy violations, all universes operate under four immutable guardrails:
1. **Read-Only Mode**: Navigation agents are prohibited from clicking "Pay Now", entering credit card details, or submitting user credentials.
2. **Strict Domain Allowlist**: Agents only navigate verified candidate domains; external redirect popups are immediately terminated.
3. **Step & Time Budgets**: Hard limits (max 15 steps / 60 seconds per universe) prevent runaway scraping loops or resource exhaustion.
4. **Human in the Loop**: The browser produces actionable links and receipts; final order confirmation is always reserved for the human user.

---

## ⚡ Quickstart & Local Demo

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.13)
- `uv` (recommended) or standard `pip`

### 2. Setup & Installation
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/multiverse-browser.git
cd multiverse-browser

# Create virtual environment and install dependencies
uv venv .venv
source .venv/bin/activate
uv pip install -r backend/requirements.txt
```

### 3. Run the Backend & Live Dashboard
```bash
# Start the FastAPI engine with built-in live dashboard and mock shops
uvicorn backend.app.main:app --reload --port 8000
```

### 4. Experience the Multiverse
1. Open **`http://localhost:8000/`** in your browser.
2. Click **"🚀 Launch Parallel Universes"**.
3. Watch the 4 universes race in parallel:
   - **Deal Hunter** discovers the secret coupon `DEAL500` on *DealNest*.
   - **Budget** catches the discovery live via Blackboard telepathy and slashes the landed cost to ₹2,299.
   - **Trust** flags the deceptive fake MRP on *FlashKart*.
   - **Budget** detects the drip fee trap on *ElectroBazaar* (advertised at ₹2,199, lands at ₹2,547).
   - The **Judge** synthesizes the verdict: **₹248 saved vs naive listing with proof receipts**.
4. Inspect the mock stores directly at **`http://localhost:8000/mock`**.

---

## 👥 Hackathon Team & Track

- **Track**: Track 2 (Beyond the Browser)
- **Institution**: Ramaiah Institute of Technology
- **Tech Stack**: Python, FastAPI, WebSockets, Playwright, React, Tailwind CSS, ElevenLabs, Amazon Bedrock & AWS S3.
