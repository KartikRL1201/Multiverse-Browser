import asyncio
import json
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from backend.app.config import settings
from backend.app.mock_shops.app import router as mock_router
from backend.app.mock_shops.multi_domain import router as portal_router
from backend.app.orchestrator import MultiverseOrchestrator
from backend.app.planner import StrategyPlanner
from backend.app.mock_shops.data import PRODUCTS

app = FastAPI(
    title="Multiverse Browser Engine",
    description="Goal-agnostic parallel browser swarm with dynamic N-universe planning and shared blackboard synchronization",
    version=settings.VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount testbed portals
app.include_router(mock_router)
app.include_router(portal_router)


class SearchRequest(BaseModel):
    query: str = "Buy wireless ANC headphones under ₹3,000 with genuine warranty and promo deals"
    target_urls: Optional[List[str]] = None


connected_websockets: List[WebSocket] = []


async def broadcast_ws(event: Dict[str, Any]):
    message = json.dumps(event)
    for ws in list(connected_websockets):
        try:
            await ws.send_text(message)
        except Exception:
            if ws in connected_websockets:
                connected_websockets.remove(ws)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "system": "Multiverse Swarm Orchestrator",
        "version": settings.VERSION,
        "planner": "dynamic_n_universes",
        "guardrails": {
            "mode": "read_only_enforced",
            "max_steps": settings.MAX_STEPS_PER_UNIVERSE,
            "timeout_seconds": settings.TIMEOUT_SECONDS_PER_UNIVERSE
        }
    }


@app.get("/api/catalog")
def get_catalog():
    return PRODUCTS


@app.post("/api/plan")
async def preview_plan(request: SearchRequest):
    planner = StrategyPlanner()
    plan = await planner.create_plan(request.query, request.target_urls)
    return plan.model_dump()


@app.post("/api/run")
async def trigger_run(request: SearchRequest):
    orchestrator = MultiverseOrchestrator(event_callback=broadcast_ws)
    verdict = await orchestrator.execute_run(request.query, request.target_urls)
    return {"status": "completed", "verdict": verdict}


@app.websocket("/ws/stream")
async def websocket_stream(websocket: WebSocket):
    await websocket.accept()
    connected_websockets.append(websocket)
    try:
        await websocket.send_text(json.dumps({
            "type": "CONNECTION_ESTABLISHED",
            "message": "Swarm telemetry link active"
        }))
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            action = payload.get("action")

            if action == "start_race":
                query = payload.get("query", "Find the best option without hidden catches")
                target_urls = payload.get("target_urls")
                orchestrator = MultiverseOrchestrator(event_callback=broadcast_ws)
                asyncio.create_task(orchestrator.execute_run(query, target_urls))

    except WebSocketDisconnect:
        if websocket in connected_websockets:
            connected_websockets.remove(websocket)


@app.get("/", response_class=HTMLResponse)
async def live_dashboard():
    """
    Editorial light-theme control board for Multiverse Browser.
    Dynamically spawns N browser tiles decided by the Strategy Planner
    across shopping, travel, scholarships, plans/bills, medicines, and courses.
    """
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multiverse Browser · Dynamic Swarm Control</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['"Plus Jakarta Sans"', '-apple-system', 'BlinkMacSystemFont', 'system-ui', 'sans-serif'],
                        mono: ['"JetBrains Mono"', 'ui-monospace', 'monospace']
                    }
                }
            }
        }
    </script>
    <style>
        body {
            background-color: #F8FAFC;
            color: #0F172A;
            background-image: radial-gradient(#CBD5E1 0.75px, transparent 0.75px);
            background-size: 20px 20px;
        }
        @keyframes scanGlow {
            0% { transform: translateY(-100%); }
            100% { transform: translateY(280%); }
        }
        .card-active {
            position: relative;
            overflow: hidden;
            border-color: #93C5FD !important;
            box-shadow: 0 4px 14px -2px rgba(37, 99, 235, 0.12);
        }
        .card-active::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; height: 35px;
            background: linear-gradient(180deg, transparent, rgba(37, 99, 235, 0.08), transparent);
            animation: scanGlow 2s infinite ease-in-out;
            pointer-events: none;
            z-index: 10;
        }
        @keyframes soundWaveLight {
            0%, 100% { height: 3px; }
            50% { height: 16px; }
        }
        .wave-bar {
            width: 3px;
            background-color: #059669;
            border-radius: 9999px;
            animation: soundWaveLight 1.1s infinite ease-in-out;
        }
        .wave-bar:nth-child(2) { animation-delay: 0.15s; }
        .wave-bar:nth-child(3) { animation-delay: 0.3s; }
        .wave-bar:nth-child(4) { animation-delay: 0.45s; }
        .wave-bar:nth-child(5) { animation-delay: 0.2s; }
        .wave-bar:nth-child(6) { animation-delay: 0.35s; }
        ::-webkit-scrollbar { width: 5px; height: 5px; }
        ::-webkit-scrollbar-track { background: #F1F5F9; }
        ::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 4px; }
    </style>
</head>
<body class="min-h-screen flex flex-col font-sans antialiased text-slate-900 selection:bg-blue-100 selection:text-blue-900">

    <!-- Top Navigation -->
    <header class="border-b border-slate-200/80 bg-white/90 backdrop-blur-md px-6 py-3.5 sticky top-0 z-50 shadow-[0_1px_3px_0_rgba(0,0,0,0.03)]">
        <div class="max-w-7xl mx-auto flex items-center justify-between">
            <div class="flex items-center space-x-3.5">
                <div class="w-8 h-8 rounded-lg bg-slate-900 flex items-center justify-center font-mono font-bold text-xs text-white shadow-sm">
                    M//B
                </div>
                <div>
                    <div class="flex items-center space-x-2">
                        <span class="text-sm font-bold tracking-tight text-slate-900">Multiverse Browser</span>
                        <span class="text-[10px] uppercase font-mono px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200 font-semibold">Dynamic N-Universe</span>
                    </div>
                    <p class="text-[11px] text-slate-500 font-medium">wHACKiest 2026 · Track 2 (Beyond the Browser)</p>
                </div>
            </div>

            <div class="flex items-center space-x-2.5">
                <div class="flex items-center space-x-2 text-[11px] font-mono px-3 py-1.5 rounded-lg bg-slate-50 border border-slate-200 text-slate-600">
                    <span id="systemLed" class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                    <span id="engineStatusText" class="font-medium text-slate-700">Engine Ready</span>
                </div>
                <a href="/portal" target="_blank" class="text-[11px] font-mono text-slate-600 hover:text-slate-900 px-3 py-1.5 rounded-lg bg-slate-50 hover:bg-slate-100 border border-slate-200 transition font-medium">
                    Multi-Domain Portals ↗
                </a>
                <a href="/mock" target="_blank" class="text-[11px] font-mono text-slate-600 hover:text-slate-900 px-3 py-1.5 rounded-lg bg-slate-50 hover:bg-slate-100 border border-slate-200 transition font-medium">
                    Mock Shops ↗
                </a>
            </div>
        </div>
    </header>

    <!-- Main Workspace -->
    <main class="flex-1 max-w-7xl w-full mx-auto p-6 space-y-5">

        <!-- Goal Specification & Use-Case Switcher -->
        <div class="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-[0_2px_8px_-2px_rgba(0,0,0,0.05)]">
            <div class="flex flex-col sm:flex-row gap-3">
                <div class="relative flex-1">
                    <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
                    </div>
                    <input id="goalInput" type="text" value="BLR to DEL trip with 15kg baggage, flexible cancellation, comparing flight vs train and promos" class="w-full pl-10 pr-4 py-2.5 bg-slate-50/70 border border-slate-200 rounded-xl text-sm font-sans focus:outline-none focus:border-blue-600 focus:bg-white text-slate-900 placeholder-slate-400 transition font-medium">
                </div>
                <button id="btnLaunch" onclick="startMultiverseRace()" class="px-6 py-2.5 bg-slate-900 hover:bg-slate-800 active:bg-slate-950 text-white font-semibold rounded-xl text-xs font-mono tracking-wide transition shadow-sm flex items-center justify-center gap-2 whitespace-nowrap">
                    <svg class="w-3.5 h-3.5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                    <span id="btnLaunchText">PLAN &amp; EXECUTE SWARM</span>
                </button>
            </div>

            <!-- Preset Web Goals Across Domains -->
            <div class="mt-3 flex flex-wrap items-center gap-2">
                <span class="text-[10px] font-mono uppercase tracking-wider text-slate-400 font-semibold mr-1">Try Goals:</span>
                <button onclick="setGoal('Buy wireless ANC headphones under ₹3,000 with genuine warranty, best value, and promo codes')" class="text-[11px] px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200/80 text-slate-700 font-medium transition">Shopping (4 Universes)</button>
                <button onclick="setGoal('BLR to DEL trip with 15kg baggage, flexible cancellation, comparing flight vs train and promos')" class="text-[11px] px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200/80 text-slate-700 font-medium transition">Travel &amp; Routes (5 Universes)</button>
                <button onclick="setGoal('Find B.Tech 2nd year scholarship under ₹6L income with no hidden bond or expired deadline')" class="text-[11px] px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200/80 text-slate-700 font-medium transition">Scholarships (4 Universes)</button>
                <button onclick="setGoal('Compare broadband plans auditing post-promo renewal surge, lock-in traps, and student discounts')" class="text-[11px] px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200/80 text-slate-700 font-medium transition">Plans &amp; Bills (3 Universes)</button>
                <button onclick="setGoal('Find Paracetamol 650mg comparing brand vs Jan Aushadhi generic and pharmacy delivery')" class="text-[11px] px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200/80 text-slate-700 font-medium transition">Medicines (3 Universes)</button>
                <button onclick="setGoal('Best free or cheap path to learn systems programming across YouTube, MOOCs, docs, and bootcamps')" class="text-[11px] px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200/80 text-slate-700 font-medium transition">Courses (3 Universes)</button>
            </div>

            <!-- Dynamic Planner Reasoning Strip -->
            <div id="plannerBanner" class="mt-3.5 pt-3 border-t border-slate-100 flex flex-wrap items-center justify-between gap-2 text-[11px] font-mono">
                <div class="flex items-center space-x-2 text-slate-600">
                    <span class="px-1.5 py-0.5 rounded bg-slate-900 text-white text-[10px] font-semibold">PLANNER</span>
                    <span id="plannerReasoning">Enter any web goal — the Strategy Planner dynamically decides how many parallel universes (N) to spawn.</span>
                </div>
                <div class="text-slate-400 font-medium">
                    Guardrails: Read-Only · Allowlist · 15 Steps/Worker
                </div>
            </div>
        </div>

        <!-- Dynamic Parallel Universes Grid (populated dynamically with N cards) -->
        <div id="universesGrid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div class="col-span-full bg-white border border-dashed border-slate-300 rounded-2xl p-10 text-center">
                <div class="text-xs font-mono text-slate-500">No active universe workers yet.</div>
                <div class="text-sm font-semibold text-slate-800 mt-1">Click <span class="font-mono text-blue-600">PLAN &amp; EXECUTE SWARM</span> to dynamically spawn N isolated Playwright browsers for your goal.</div>
            </div>
        </div>

        <!-- Lower Section: Shared Blackboard Bus & Synthesized Verdict -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">
            
            <!-- Left: Shared Blackboard Bus -->
            <div class="lg:col-span-5 bg-white border border-slate-200/90 rounded-2xl p-4 flex flex-col h-[360px] shadow-sm">
                <div class="flex items-center justify-between pb-3 border-b border-slate-100">
                    <div class="flex items-center space-x-2">
                        <span class="w-2 h-2 rounded-full bg-blue-600"></span>
                        <h3 class="text-xs font-bold text-slate-900 tracking-tight font-mono uppercase">Shared Blackboard Bus</h3>
                    </div>
                    <span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 border border-slate-200 font-medium">CROSS-UNIVERSE SYNC</span>
                </div>

                <div id="blackboardFeed" class="flex-1 overflow-y-auto space-y-2 mt-3 pr-1 text-[11px] font-mono">
                    <div class="text-slate-400 italic py-12 text-center text-xs">
                        Shared state channel idle. Universes broadcast vouchers, catches, eligibility blocks, and deadlines here mid-run.
                    </div>
                </div>
            </div>

            <!-- Right: Synthesized Verdict -->
            <div class="lg:col-span-7 bg-white border border-slate-200/90 rounded-2xl p-5 flex flex-col justify-between min-h-[360px] shadow-sm">
                <div>
                    <div class="flex items-center justify-between pb-3 border-b border-slate-100">
                        <div class="flex items-center space-x-2.5">
                            <span class="w-2.5 h-2.5 rounded-full bg-slate-300" id="judgeDot"></span>
                            <h3 class="text-xs font-bold text-slate-900 tracking-tight font-mono uppercase">Multiverse Judge Synthesis</h3>
                            <span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200 font-semibold">Bedrock + S3 Receipts</span>
                        </div>
                        <span id="verdictStatus" class="text-[11px] font-mono text-slate-500 font-medium">Awaiting Swarm Run</span>
                    </div>

                    <div id="verdictContent" class="mt-4">
                        <div class="p-8 rounded-xl border border-dashed border-slate-200 bg-slate-50/60 text-center text-slate-500 text-xs font-mono">
                            The Judge merges evidence across whichever N universes ran, reconciles hidden catches against headline claims, and produces one verified verdict.
                        </div>
                    </div>
                </div>

                <!-- Spoken Verdict Dock -->
                <div id="verdictAudioBox" class="mt-4 pt-3.5 border-t border-slate-100 hidden flex items-center justify-between">
                    <div class="flex items-center space-x-3 text-xs">
                        <div class="flex items-center space-x-1 h-5 px-2 bg-emerald-50 border border-emerald-200 rounded-md">
                            <div class="wave-bar"></div><div class="wave-bar"></div><div class="wave-bar"></div>
                            <div class="wave-bar"></div><div class="wave-bar"></div><div class="wave-bar"></div>
                        </div>
                        <div class="font-mono text-[11px]">
                            <span class="text-emerald-700 font-semibold">ElevenLabs TTS:</span>
                            <span id="verdictAudioText" class="text-slate-600 ml-1.5 truncate max-w-sm inline-block align-bottom font-medium"></span>
                        </div>
                    </div>
                    <button onclick="playSampleAudio()" class="px-3.5 py-1.5 bg-slate-900 hover:bg-slate-800 text-white text-xs font-mono font-medium rounded-lg transition shadow-sm flex items-center gap-1.5">
                        <svg class="w-3 h-3 text-emerald-400" fill="currentColor" viewBox="0 0 20 20"><path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z"/></svg>
                        <span>Play Verdict</span>
                    </button>
                </div>
            </div>
        </div>
    </main>

    <script>
        let socket;
        function connectWS() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            socket = new WebSocket(`${protocol}//${window.location.host}/ws/stream`);

            socket.onopen = () => {
                document.getElementById('systemLed').className = 'w-2 h-2 rounded-full bg-emerald-500 animate-pulse';
                document.getElementById('engineStatusText').innerText = 'Telemetry Connected';
            };
            socket.onmessage = (event) => handleEvent(JSON.parse(event.data));
            socket.onclose = () => {
                document.getElementById('systemLed').className = 'w-2 h-2 rounded-full bg-rose-500';
                document.getElementById('engineStatusText').innerText = 'Reconnecting...';
                setTimeout(connectWS, 2000);
            };
        }

        function setGoal(text) {
            document.getElementById('goalInput').value = text;
        }

        function renderDynamicUniverseGrid(plan) {
            const grid = document.getElementById('universesGrid');
            const n = plan.universe_count;
            // Responsive grid adapted dynamically to N universes
            grid.className = n === 4
                ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4'
                : n === 3
                ? 'grid grid-cols-1 md:grid-cols-3 gap-4'
                : 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4';

            document.getElementById('plannerReasoning').innerHTML =
                `<span class="font-bold text-slate-900 uppercase">[${plan.domain}]</span> Spawned <span class="font-bold text-blue-600">${n} universes</span> — ${plan.reasoning}`;

            grid.innerHTML = plan.universes.map((u, idx) => `
                <div id="card-${u.universe_id}" class="bg-white border border-slate-200/90 rounded-2xl flex flex-col justify-between transition-all duration-300 overflow-hidden shadow-sm">
                    <div>
                        <div class="px-3.5 py-2.5 border-b border-slate-100 bg-slate-50/80 flex items-center justify-between">
                            <div class="flex items-center space-x-1.5">
                                <span class="w-2 h-2 rounded-full bg-rose-400"></span>
                                <span class="w-2 h-2 rounded-full bg-amber-400"></span>
                                <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
                                <span class="ml-1.5 text-[10px] font-mono uppercase tracking-wider text-slate-500 font-bold">U0${idx + 1}</span>
                            </div>
                            <span id="badge-${u.universe_id}" class="text-[9px] font-mono px-2 py-0.5 rounded-md bg-slate-100 text-slate-600 font-semibold border border-slate-200">SPAWNED</span>
                        </div>

                        <div class="p-3.5">
                            <div class="flex items-baseline justify-between gap-2">
                                <h3 class="text-xs font-bold text-slate-900 tracking-tight truncate">${u.title}</h3>
                                <span class="text-[10px] font-mono text-slate-400 font-medium shrink-0" id="step-${u.universe_id}">Step 00/15</span>
                            </div>
                            <p class="text-[11px] text-slate-500 mt-0.5 line-clamp-2">${u.strategy}</p>

                            <div class="mt-2.5 px-2.5 py-1 bg-slate-100/80 rounded-lg border border-slate-200/70 text-[10px] font-mono text-slate-600 truncate font-medium" id="url-${u.universe_id}">
                                browser://initializing
                            </div>

                            <!-- Live Playwright Screenshot Preview -->
                            <div id="shotbox-${u.universe_id}" class="mt-2.5 h-24 rounded-lg border border-slate-200/80 bg-slate-50 overflow-hidden flex items-center justify-center">
                                <span class="text-[10px] font-mono text-slate-400">Waiting for Playwright frame...</span>
                            </div>

                            <div class="mt-2.5 p-2.5 bg-slate-50 rounded-xl border border-slate-200/80 min-h-[62px]">
                                <div id="action-${u.universe_id}" class="text-[11px] font-mono text-slate-700 line-clamp-3 font-medium">
                                    Initializing isolated browser context...
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="px-3.5 py-2.5 border-t border-slate-100 bg-slate-50/60 flex justify-between items-baseline">
                        <span class="text-[11px] font-mono text-slate-500 font-medium">${u.metric_label}:</span>
                        <span id="metric-${u.universe_id}" class="text-sm font-mono font-bold text-slate-400">--</span>
                    </div>
                </div>
            `).join('');
        }

        function handleEvent(e) {
            if (e.type === 'PLAN_GENERATED') {
                renderDynamicUniverseGrid(e);
                return;
            }

            if (e.universe) {
                const u = e.universe;
                const card = document.getElementById(`card-${u}`);
                const actionElem = document.getElementById(`action-${u}`);
                const badgeElem = document.getElementById(`badge-${u}`);
                const metricElem = document.getElementById(`metric-${u}`);
                const stepElem = document.getElementById(`step-${u}`);
                const urlElem = document.getElementById(`url-${u}`);
                const shotBox = document.getElementById(`shotbox-${u}`);

                if (actionElem) actionElem.innerText = e.action;
                if (stepElem && e.step) stepElem.innerText = `Step ${String(e.step).padStart(2, '0')}/15`;
                if (urlElem && e.target_url) urlElem.innerText = e.target_url.replace('http://127.0.0.1:8000', '');
                if (shotBox && e.screenshot) {
                    shotBox.innerHTML = `<img src="${e.screenshot}" alt="Live DOM frame" class="w-full h-full object-cover object-top" />`;
                }

                if (badgeElem) {
                    badgeElem.innerText = e.status.toUpperCase();
                    if (e.status === 'running') {
                        badgeElem.className = 'text-[9px] font-mono px-2 py-0.5 rounded-md bg-blue-50 text-blue-700 border border-blue-200 font-semibold';
                        if (card) card.classList.add('card-active');
                    } else if (e.status === 'discovery') {
                        badgeElem.className = 'text-[9px] font-mono px-2 py-0.5 rounded-md bg-amber-50 text-amber-700 border border-amber-200 font-semibold';
                    } else if (e.status === 'flagged') {
                        badgeElem.className = 'text-[9px] font-mono px-2 py-0.5 rounded-md bg-rose-50 text-rose-700 border border-rose-200 font-semibold';
                    } else if (e.status === 'completed') {
                        badgeElem.className = 'text-[9px] font-mono px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-700 border border-emerald-200 font-semibold';
                        if (card) card.classList.remove('card-active');
                    }
                }

                const disp = (e.metadata && e.metadata.metric_display) || (e.found_price ? `₹${e.found_price.toLocaleString('en-IN')}` : null);
                if (metricElem && disp && disp !== '--') {
                    metricElem.innerText = disp;
                    metricElem.classList.remove('text-slate-400');
                    metricElem.classList.add('text-slate-900');
                }
            }

            if (e.type === 'COUPON_DISCOVERED') {
                addBlackboardEntry('VOUCHER_SYNC', 'amber', `[${e.universe}] Extracted '${e.code}' on ${e.site} (${e.discount_text})`);
            } else if (e.type === 'DARK_PATTERN_FLAGGED') {
                addBlackboardEntry(e.pattern_type || 'CATCH_ALERT', 'rose', e.details);
            } else if (e.type === 'BLACKBOARD_FINDING') {
                const tone = e.severity === 'high' ? 'rose' : e.severity === 'positive' ? 'emerald' : 'blue';
                addBlackboardEntry(e.category, tone, e.details);
            } else if (e.type === 'JUDGE_EVALUATING') {
                document.getElementById('judgeDot').className = 'w-2.5 h-2.5 rounded-full bg-blue-600 animate-ping';
                document.getElementById('verdictStatus').innerText = 'JUDGE SYNTHESIZING...';
                document.getElementById('verdictStatus').className = 'text-[11px] font-mono text-blue-600 font-bold';
            } else if (e.type === 'VERDICT_FINALIZED') {
                renderVerdict(e.verdict);
            }
        }

        function addBlackboardEntry(tag, tone, text) {
            const feed = document.getElementById('blackboardFeed');
            const placeholder = feed.querySelector('.italic');
            if (placeholder) placeholder.remove();

            const styles = {
                rose: 'border-rose-200 bg-rose-50/60 text-rose-900',
                amber: 'border-amber-200 bg-amber-50/60 text-amber-900',
                emerald: 'border-emerald-200 bg-emerald-50/60 text-emerald-900',
                blue: 'border-blue-200 bg-blue-50/60 text-blue-900'
            };
            const tagStyles = {
                rose: 'bg-rose-100 text-rose-700 border-rose-300',
                amber: 'bg-amber-100 text-amber-700 border-amber-300',
                emerald: 'bg-emerald-100 text-emerald-700 border-emerald-300',
                blue: 'bg-blue-100 text-blue-700 border-blue-300'
            };

            const now = new Date().toTimeString().split(' ')[0];
            const item = document.createElement('div');
            item.className = `p-2.5 rounded-xl border ${styles[tone] || styles.blue} flex items-start space-x-2 shadow-sm`;
            item.innerHTML = `
                <span class="text-slate-400 select-none text-[10px] font-mono shrink-0">${now}</span>
                <span class="px-1.5 py-0.2 rounded text-[9px] font-semibold border shrink-0 ${tagStyles[tone] || tagStyles.blue}">${tag}</span>
                <span class="flex-1 text-slate-800 text-[11px] font-medium leading-relaxed">${text}</span>
            `;
            feed.prepend(item);
        }

        function renderVerdict(v) {
            document.getElementById('judgeDot').className = 'w-2.5 h-2.5 rounded-full bg-emerald-500';
            document.getElementById('verdictStatus').innerText = 'VERDICT FINALIZED';
            document.getElementById('verdictStatus').className = 'text-[11px] font-mono text-emerald-600 font-bold';

            const w = v.winner;
            let catchesHtml = '';
            if (v.dark_patterns_avoided && v.dark_patterns_avoided.length > 0) {
                catchesHtml = v.dark_patterns_avoided.map(dp => `
                    <div class="p-2.5 bg-rose-50/60 border border-rose-200/80 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-1 text-[11px] font-sans">
                        <span class="text-rose-800 font-semibold font-mono">✕ ${dp.store}: ${dp.pattern}</span>
                        <span class="text-rose-700 text-[11px] font-medium">${dp.impact}</span>
                    </div>
                `).join('');
            } else {
                catchesHtml = `<div class="p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-[11px] text-slate-600">No hidden catches flagged in final synthesis.</div>`;
            }

            document.getElementById('verdictContent').innerHTML = `
                <div class="bg-white border border-slate-200 rounded-xl p-5 space-y-4 font-mono shadow-sm">
                    <div class="flex items-center justify-between border-b border-slate-100 pb-3.5">
                        <div>
                            <span class="text-[10px] text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200 font-bold uppercase tracking-wider">${w.winning_universe}</span>
                            <div class="text-base font-sans font-bold text-slate-900 mt-1">${w.title}</div>
                            <div class="text-[11px] text-slate-500 font-medium font-sans">Provider: <span class="text-slate-900 font-bold">${w.provider}</span> · Domain: ${v.domain}</div>
                        </div>
                        <div class="text-right">
                            <div class="text-[10px] text-slate-400 uppercase font-semibold">Confidence</div>
                            <div class="text-base font-bold text-emerald-600">${Math.round(w.confidence_score * 100)}%</div>
                        </div>
                    </div>

                    <div class="grid grid-cols-3 gap-2 py-1 text-center font-mono">
                        <div class="p-2.5 bg-slate-50 rounded-xl border border-slate-200/80">
                            <div class="text-[10px] text-slate-400 font-semibold">${w.surface_metric_label}</div>
                            <div class="text-xs font-bold text-slate-700 mt-0.5">${w.surface_metric_value}</div>
                        </div>
                        <div class="p-2.5 bg-amber-50/70 rounded-xl border border-amber-200/80">
                            <div class="text-[10px] text-amber-600 font-semibold">${w.offset_label}</div>
                            <div class="text-xs font-bold text-amber-700 mt-0.5">${w.offset_value}</div>
                        </div>
                        <div class="p-2.5 bg-emerald-50 rounded-xl border border-emerald-200">
                            <div class="text-[10px] text-emerald-600 font-semibold">${w.final_metric_label}</div>
                            <div class="text-xs font-bold text-emerald-700 mt-0.5">${w.final_metric_value}</div>
                        </div>
                    </div>

                    <div class="p-3 rounded-xl bg-emerald-50/80 border border-emerald-200 text-xs font-sans text-emerald-900 font-semibold">
                        ✓ ${w.savings_headline}
                    </div>

                    <div class="pt-1">
                        <div class="text-[10px] text-slate-400 uppercase tracking-wider mb-2 font-bold font-mono">Hidden Catches &amp; Fine Print Uncovered</div>
                        <div class="space-y-2">${catchesHtml}</div>
                    </div>
                </div>
            `;

            document.getElementById('verdictAudioBox').classList.remove('hidden');
            document.getElementById('verdictAudioText').innerText = v.spoken_summary;
            document.getElementById('btnLaunch').disabled = false;
            document.getElementById('btnLaunchText').innerText = 'PLAN & EXECUTE SWARM';
        }

        function playSampleAudio() {
            const u = new SpeechSynthesisUtterance(document.getElementById('verdictAudioText').innerText);
            u.rate = 1.05;
            window.speechSynthesis.speak(u);
        }

        function startMultiverseRace() {
            const query = document.getElementById('goalInput').value;
            document.getElementById('blackboardFeed').innerHTML = '';
            document.getElementById('verdictContent').innerHTML = `
                <div class="p-8 rounded-xl border border-blue-200 bg-blue-50/50 text-center text-blue-700 text-xs font-mono space-y-2">
                    <div class="inline-block w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                    <div class="font-medium">Planner sizing universes &amp; launching parallel Playwright contexts...</div>
                </div>
            `;
            document.getElementById('verdictStatus').innerText = 'SWARM ACTIVE';
            document.getElementById('verdictStatus').className = 'text-[11px] font-mono text-blue-600 font-bold';
            document.getElementById('btnLaunch').disabled = true;
            document.getElementById('btnLaunchText').innerText = 'RUNNING...';

            if (socket && socket.readyState === WebSocket.OPEN) {
                socket.send(JSON.stringify({ action: 'start_race', query: query }));
            }
        }

        window.onload = connectWS;
    </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content)
