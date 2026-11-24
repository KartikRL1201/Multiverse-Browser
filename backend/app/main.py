import asyncio
import json
from typing import List, Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from backend.app.config import settings
from backend.app.mock_shops.app import router as mock_router
from backend.app.orchestrator import MultiverseOrchestrator
from backend.app.mock_shops.data import PRODUCTS

app = FastAPI(
    title="Multiverse Browser Engine",
    description="Autonomous parallel browser agent swarm with shared blackboard synchronization",
    version=settings.VERSION
)

# Enable CORS for external frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Mock Shops router
app.include_router(mock_router)

class SearchRequest(BaseModel):
    query: str = "wireless noise cancelling headphones under 3000"
    target_urls: List[str] = [
        "http://localhost:8000/mock/electrobazaar/soundpulse-500",
        "http://localhost:8000/mock/dealnest/soundpulse-500",
        "http://localhost:8000/mock/flashkart/soundpulse-500"
    ]

# Active WebSocket connections
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
        "guardrails": {
            "mode": "read_only_enforced",
            "max_steps": settings.MAX_STEPS_PER_UNIVERSE,
            "timeout_seconds": settings.TIMEOUT_SECONDS_PER_UNIVERSE
        }
    }

@app.get("/api/catalog")
def get_catalog():
    return PRODUCTS

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
                query = payload.get("query", "wireless headphones under 3000")
                target_urls = payload.get("target_urls", [
                    "http://localhost:8000/mock/electrobazaar/soundpulse-500",
                    "http://localhost:8000/mock/dealnest/soundpulse-500",
                    "http://localhost:8000/mock/flashkart/soundpulse-500"
                ])
                orchestrator = MultiverseOrchestrator(event_callback=broadcast_ws)
                asyncio.create_task(orchestrator.execute_run(query, target_urls))
                
    except WebSocketDisconnect:
        if websocket in connected_websockets:
            connected_websockets.remove(websocket)

@app.get("/", response_class=HTMLResponse)
async def live_dashboard():
    """
    Sleek, editorial light-theme engineering dashboard for Multiverse Browser.
    Minimalist white palette, refined typography, authentic browser session frames,
    and real-time blackboard synchronization.
    """
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multiverse Browser · Swarm Control</title>
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
                    },
                    colors: {
                        canvas: '#F8FAFC',
                        surface: '#FFFFFF',
                        borderMuted: '#E2E8F0',
                        borderHover: '#CBD5E1',
                        ink: '#0F172A',
                        slateSubtle: '#64748B',
                        brandBlue: '#2563EB',
                        brandEmerald: '#059669',
                        brandAmber: '#D97706',
                        brandRose: '#E11D48'
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

        /* Subtle scanning beam for active card */
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
        }

        /* Audio Waveform */
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

        /* Custom scrollbar */
        ::-webkit-scrollbar { width: 5px; height: 5px; }
        ::-webkit-scrollbar-track { background: #F1F5F9; }
        ::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #94A3B8; }
    </style>
</head>
<body class="min-h-screen flex flex-col font-sans antialiased text-slate-900 selection:bg-blue-100 selection:text-blue-900">

    <!-- Top Command Navigation -->
    <header class="border-b border-slate-200/80 bg-white/90 backdrop-blur-md px-6 py-3.5 sticky top-0 z-50 shadow-[0_1px_3px_0_rgba(0,0,0,0.03)]">
        <div class="max-w-7xl mx-auto flex items-center justify-between">
            <div class="flex items-center space-x-3.5">
                <div class="w-8 h-8 rounded-lg bg-slate-900 flex items-center justify-center font-mono font-bold text-xs text-white shadow-sm">
                    M//B
                </div>
                <div>
                    <div class="flex items-center space-x-2">
                        <span class="text-sm font-bold tracking-tight text-slate-900">Multiverse Browser</span>
                        <span class="text-[10px] uppercase font-mono px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200 font-semibold">v0.1.0-mvp</span>
                    </div>
                    <p class="text-[11px] text-slate-500 font-medium">wHACKiest 2026 · Track 2 (Beyond the Browser)</p>
                </div>
            </div>

            <!-- System Metrics & Telemetry Status -->
            <div class="flex items-center space-x-3">
                <div class="flex items-center space-x-2 text-[11px] font-mono px-3 py-1.5 rounded-lg bg-slate-50 border border-slate-200 text-slate-600">
                    <span id="systemLed" class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                    <span id="engineStatusText" class="font-medium text-slate-700">Swarm Engine Ready</span>
                </div>
                <a href="/mock" target="_blank" class="text-[11px] font-mono text-slate-600 hover:text-slate-900 px-3 py-1.5 rounded-lg bg-slate-50 hover:bg-slate-100 border border-slate-200 transition flex items-center gap-1.5 font-medium">
                    <span>Inspect Seed Stores</span>
                    <svg class="w-3 h-3 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
                </a>
            </div>
        </div>
    </header>

    <!-- Main Workspace -->
    <main class="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">

        <!-- Command Input / Intent Specification -->
        <div class="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-[0_2px_8px_-2px_rgba(0,0,0,0.05)] relative">
            <div class="flex flex-col sm:flex-row gap-3">
                <div class="relative flex-1">
                    <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
                    </div>
                    <input id="goalInput" type="text" value="Find wireless ANC headphones under ₹3,000" class="w-full pl-10 pr-4 py-2.5 bg-slate-50/70 border border-slate-200 rounded-xl text-sm font-sans focus:outline-none focus:border-blue-600 focus:bg-white text-slate-900 placeholder-slate-400 transition font-medium">
                </div>
                <button id="btnLaunch" onclick="startMultiverseRace()" class="px-6 py-2.5 bg-slate-900 hover:bg-slate-800 active:bg-slate-950 text-white font-semibold rounded-xl text-xs font-mono tracking-wide transition shadow-sm flex items-center justify-center gap-2">
                    <svg id="launchIcon" class="w-3.5 h-3.5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                    <span id="btnLaunchText">EXECUTE SWARM</span>
                </button>
            </div>
            
            <!-- Guardrails Metadata Pill Bar -->
            <div class="mt-3.5 pt-3 border-t border-slate-100 flex flex-wrap items-center justify-between text-[11px] font-mono text-slate-500">
                <div class="flex items-center space-x-3">
                    <span class="text-slate-400 font-semibold">Guardrails:</span>
                    <span class="inline-flex items-center gap-1.5 text-slate-700 font-medium">
                        <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span> Read-Only Enforced
                    </span>
                    <span class="text-slate-300">·</span>
                    <span class="text-slate-600">Domain Allowlist: 3 Sites</span>
                    <span class="text-slate-300">·</span>
                    <span class="text-slate-600">Step Budget: 15 / Worker</span>
                </div>
                <div id="targetUrlCounter" class="text-slate-400 font-medium">
                    Testbed: 3 Seed Stores Initialized
                </div>
            </div>
        </div>

        <!-- 4 Parallel Browser Universes Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            
            <!-- Universe 1: Budget / True Cost -->
            <div id="card-budget" class="bg-white border border-slate-200/90 rounded-2xl flex flex-col justify-between transition-all duration-300 overflow-hidden shadow-sm hover:shadow-md">
                <div>
                    <!-- Browser Window Chrome -->
                    <div class="px-3.5 py-2.5 border-b border-slate-100 bg-slate-50/80 flex items-center justify-between">
                        <div class="flex items-center space-x-1.5">
                            <span class="w-2.5 h-2.5 rounded-full bg-rose-400"></span>
                            <span class="w-2.5 h-2.5 rounded-full bg-amber-400"></span>
                            <span class="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
                            <span class="ml-2 text-[10px] font-mono uppercase tracking-wider text-slate-500 font-bold">Universe 01</span>
                        </div>
                        <span id="badge-budget" class="text-[9px] font-mono px-2 py-0.5 rounded-md bg-slate-100 text-slate-600 font-semibold border border-slate-200">IDLE</span>
                    </div>

                    <!-- Inner Card Header -->
                    <div class="p-4">
                        <div class="flex items-baseline justify-between">
                            <h3 class="text-xs font-bold text-slate-900 tracking-tight">Landed Cost Auditor</h3>
                            <span class="text-[10px] font-mono text-slate-400 font-medium" id="step-budget">Step --/15</span>
                        </div>
                        <p class="text-[11px] text-slate-500 mt-0.5">Navigates to checkout to detect drip fees.</p>

                        <!-- Simulated Address Bar -->
                        <div class="mt-3 px-2.5 py-1 bg-slate-100/80 rounded-lg border border-slate-200/70 text-[10px] font-mono text-slate-600 truncate font-medium" id="url-budget">
                            mock://awaiting-session
                        </div>

                        <!-- Live Action Terminal -->
                        <div class="mt-3 p-3 bg-slate-50 rounded-xl border border-slate-200/80 min-h-[85px] flex flex-col justify-between">
                            <div class="text-[10px] font-mono text-slate-400 font-semibold uppercase tracking-wider">DOM Activity:</div>
                            <div id="action-budget" class="text-[11px] font-mono text-slate-700 mt-1 line-clamp-3 font-medium">
                                Standby for query execution...
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Footer Metric -->
                <div class="p-3.5 border-t border-slate-100 bg-slate-50/60 flex justify-between items-baseline">
                    <span class="text-[11px] font-mono text-slate-500 font-medium">Landed Price:</span>
                    <span id="price-budget" class="text-base font-mono font-bold text-slate-400">--</span>
                </div>
            </div>

            <!-- Universe 2: Deal Hunter -->
            <div id="card-deal_hunter" class="bg-white border border-slate-200/90 rounded-2xl flex flex-col justify-between transition-all duration-300 overflow-hidden shadow-sm hover:shadow-md">
                <div>
                    <!-- Browser Window Chrome -->
                    <div class="px-3.5 py-2.5 border-b border-slate-100 bg-slate-50/80 flex items-center justify-between">
                        <div class="flex items-center space-x-1.5">
                            <span class="w-2.5 h-2.5 rounded-full bg-rose-400"></span>
                            <span class="w-2.5 h-2.5 rounded-full bg-amber-400"></span>
                            <span class="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
                            <span class="ml-2 text-[10px] font-mono uppercase tracking-wider text-slate-500 font-bold">Universe 02</span>
                        </div>
                        <span id="badge-deal_hunter" class="text-[9px] font-mono px-2 py-0.5 rounded-md bg-slate-100 text-slate-600 font-semibold border border-slate-200">IDLE</span>
                    </div>

                    <!-- Inner Card Header -->
                    <div class="p-4">
                        <div class="flex items-baseline justify-between">
                            <h3 class="text-xs font-bold text-slate-900 tracking-tight">Voucher & Code Scraper</h3>
                            <span class="text-[10px] font-mono text-slate-400 font-medium" id="step-deal_hunter">Step --/15</span>
                        </div>
                        <p class="text-[11px] text-slate-500 mt-0.5">Scrapes promotional banners and hidden footers.</p>

                        <!-- Simulated Address Bar -->
                        <div class="mt-3 px-2.5 py-1 bg-slate-100/80 rounded-lg border border-slate-200/70 text-[10px] font-mono text-slate-600 truncate font-medium" id="url-deal_hunter">
                            mock://awaiting-session
                        </div>

                        <!-- Live Action Terminal -->
                        <div class="mt-3 p-3 bg-slate-50 rounded-xl border border-slate-200/80 min-h-[85px] flex flex-col justify-between">
                            <div class="text-[10px] font-mono text-slate-400 font-semibold uppercase tracking-wider">DOM Activity:</div>
                            <div id="action-deal_hunter" class="text-[11px] font-mono text-slate-700 mt-1 line-clamp-3 font-medium">
                                Standby for query execution...
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Footer Metric -->
                <div class="p-3.5 border-t border-slate-100 bg-slate-50/60 flex justify-between items-baseline">
                    <span class="text-[11px] font-mono text-slate-500 font-medium">Extracted Voucher:</span>
                    <span id="price-deal_hunter" class="text-base font-mono font-bold text-slate-400">--</span>
                </div>
            </div>

            <!-- Universe 3: Trust & Signals -->
            <div id="card-trust" class="bg-white border border-slate-200/90 rounded-2xl flex flex-col justify-between transition-all duration-300 overflow-hidden shadow-sm hover:shadow-md">
                <div>
                    <!-- Browser Window Chrome -->
                    <div class="px-3.5 py-2.5 border-b border-slate-100 bg-slate-50/80 flex items-center justify-between">
                        <div class="flex items-center space-x-1.5">
                            <span class="w-2.5 h-2.5 rounded-full bg-rose-400"></span>
                            <span class="w-2.5 h-2.5 rounded-full bg-amber-400"></span>
                            <span class="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
                            <span class="ml-2 text-[10px] font-mono uppercase tracking-wider text-slate-500 font-bold">Universe 03</span>
                        </div>
                        <span id="badge-trust" class="text-[9px] font-mono px-2 py-0.5 rounded-md bg-slate-100 text-slate-600 font-semibold border border-slate-200">IDLE</span>
                    </div>

                    <!-- Inner Card Header -->
                    <div class="p-4">
                        <div class="flex items-baseline justify-between">
                            <h3 class="text-xs font-bold text-slate-900 tracking-tight">Authenticity Auditor</h3>
                            <span class="text-[10px] font-mono text-slate-400 font-medium" id="step-trust">Step --/15</span>
                        </div>
                        <p class="text-[11px] text-slate-500 mt-0.5">Audits warranties and flags deceptive MRP claims.</p>

                        <!-- Simulated Address Bar -->
                        <div class="mt-3 px-2.5 py-1 bg-slate-100/80 rounded-lg border border-slate-200/70 text-[10px] font-mono text-slate-600 truncate font-medium" id="url-trust">
                            mock://awaiting-session
                        </div>

                        <!-- Live Action Terminal -->
                        <div class="mt-3 p-3 bg-slate-50 rounded-xl border border-slate-200/80 min-h-[85px] flex flex-col justify-between">
                            <div class="text-[10px] font-mono text-slate-400 font-semibold uppercase tracking-wider">DOM Activity:</div>
                            <div id="action-trust" class="text-[11px] font-mono text-slate-700 mt-1 line-clamp-3 font-medium">
                                Standby for query execution...
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Footer Metric -->
                <div class="p-3.5 border-t border-slate-100 bg-slate-50/60 flex justify-between items-baseline">
                    <span class="text-[11px] font-mono text-slate-500 font-medium">Trust Index:</span>
                    <span id="price-trust" class="text-base font-mono font-bold text-slate-400">--</span>
                </div>
            </div>

            <!-- Universe 4: Best Value -->
            <div id="card-value" class="bg-white border border-slate-200/90 rounded-2xl flex flex-col justify-between transition-all duration-300 overflow-hidden shadow-sm hover:shadow-md">
                <div>
                    <!-- Browser Window Chrome -->
                    <div class="px-3.5 py-2.5 border-b border-slate-100 bg-slate-50/80 flex items-center justify-between">
                        <div class="flex items-center space-x-1.5">
                            <span class="w-2.5 h-2.5 rounded-full bg-rose-400"></span>
                            <span class="w-2.5 h-2.5 rounded-full bg-amber-400"></span>
                            <span class="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
                            <span class="ml-2 text-[10px] font-mono uppercase tracking-wider text-slate-500 font-bold">Universe 04</span>
                        </div>
                        <span id="badge-value" class="text-[9px] font-mono px-2 py-0.5 rounded-md bg-slate-100 text-slate-600 font-semibold border border-slate-200">IDLE</span>
                    </div>

                    <!-- Inner Card Header -->
                    <div class="p-4">
                        <div class="flex items-baseline justify-between">
                            <h3 class="text-xs font-bold text-slate-900 tracking-tight">Feature / Cost Matrix</h3>
                            <span class="text-[10px] font-mono text-slate-400 font-medium" id="step-value">Step --/15</span>
                        </div>
                        <p class="text-[11px] text-slate-500 mt-0.5">Calculates ANC specs, battery & sentiment trade-offs.</p>

                        <!-- Simulated Address Bar -->
                        <div class="mt-3 px-2.5 py-1 bg-slate-100/80 rounded-lg border border-slate-200/70 text-[10px] font-mono text-slate-600 truncate font-medium" id="url-value">
                            mock://awaiting-session
                        </div>

                        <!-- Live Action Terminal -->
                        <div class="mt-3 p-3 bg-slate-50 rounded-xl border border-slate-200/80 min-h-[85px] flex flex-col justify-between">
                            <div class="text-[10px] font-mono text-slate-400 font-semibold uppercase tracking-wider">DOM Activity:</div>
                            <div id="action-value" class="text-[11px] font-mono text-slate-700 mt-1 line-clamp-3 font-medium">
                                Standby for query execution...
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Footer Metric -->
                <div class="p-3.5 border-t border-slate-100 bg-slate-50/60 flex justify-between items-baseline">
                    <span class="text-[11px] font-mono text-slate-500 font-medium">Value Rating:</span>
                    <span id="price-value" class="text-base font-mono font-bold text-slate-400">--</span>
                </div>
            </div>
        </div>

        <!-- Lower Section: Shared Intelligence Bus & Final Synthesized Ledger -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">
            
            <!-- Left: Shared State Bus (Blackboard) -->
            <div class="lg:col-span-5 bg-white border border-slate-200/90 rounded-2xl p-4 flex flex-col h-[340px] shadow-sm">
                <div class="flex items-center justify-between pb-3 border-b border-slate-100">
                    <div class="flex items-center space-x-2">
                        <span class="w-2 h-2 rounded-full bg-blue-600"></span>
                        <h3 class="text-xs font-bold text-slate-900 tracking-tight font-mono uppercase">Shared Blackboard Bus</h3>
                    </div>
                    <span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 border border-slate-200 font-medium">CROSS-AGENT MEMORY</span>
                </div>

                <!-- Realtime Feed -->
                <div id="blackboardFeed" class="flex-1 overflow-y-auto space-y-2 mt-3 pr-1 text-[11px] font-mono">
                    <div class="text-slate-400 italic py-10 text-center text-xs">
                        Shared state channel idle. Launch swarm to observe cross-agent discovery exchange.
                    </div>
                </div>
            </div>

            <!-- Right: Synthesized Verdict & Financial Reconciliation -->
            <div class="lg:col-span-7 bg-white border border-slate-200/90 rounded-2xl p-5 flex flex-col justify-between min-h-[340px] shadow-sm">
                <div>
                    <div class="flex items-center justify-between pb-3 border-b border-slate-100">
                        <div class="flex items-center space-x-2.5">
                            <span class="w-2.5 h-2.5 rounded-full bg-slate-300" id="judgeDot"></span>
                            <h3 class="text-xs font-bold text-slate-900 tracking-tight font-mono uppercase">Multiverse Judge Synthesis</h3>
                            <span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200 font-semibold">AWS Bedrock + S3</span>
                        </div>
                        <span id="verdictStatus" class="text-[11px] font-mono text-slate-500 font-medium">Awaiting Swarm Run</span>
                    </div>

                    <!-- Dynamic Verdict Card -->
                    <div id="verdictContent" class="mt-4">
                        <div class="p-8 rounded-xl border border-dashed border-slate-200 bg-slate-50/60 text-center text-slate-500 text-xs font-mono">
                            The central Bedrock Judge will aggregate DOM screenshot receipts, reconcile true landed costs against surface listings, and produce a verified recommendation ledger.
                        </div>
                    </div>
                </div>

                <!-- Spoken Verdict Playback Dock -->
                <div id="verdictAudioBox" class="mt-4 pt-3.5 border-t border-slate-100 hidden flex items-center justify-between">
                    <div class="flex items-center space-x-3 text-xs">
                        <div class="flex items-center space-x-1 h-5 px-2 bg-emerald-50 border border-emerald-200 rounded-md">
                            <div class="wave-bar"></div>
                            <div class="wave-bar"></div>
                            <div class="wave-bar"></div>
                            <div class="wave-bar"></div>
                            <div class="wave-bar"></div>
                            <div class="wave-bar"></div>
                        </div>
                        <div class="font-mono text-[11px]">
                            <span class="text-emerald-700 font-semibold">ElevenLabs Voice:</span>
                            <span id="verdictAudioText" class="text-slate-600 ml-1.5 truncate max-w-sm inline-block align-bottom font-medium"></span>
                        </div>
                    </div>
                    <button onclick="playSampleAudio()" class="px-3.5 py-1.5 bg-slate-900 hover:bg-slate-800 text-white text-xs font-mono font-medium rounded-lg transition shadow-sm flex items-center gap-1.5">
                        <svg class="w-3 h-3 text-emerald-400" fill="currentColor" viewBox="0 0 20 20"><path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z"/></svg>
                        <span>Play Spoken Verdict</span>
                    </button>
                </div>
            </div>
        </div>
    </main>

    <!-- Client Script -->
    <script>
        let socket;
        function connectWS() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            socket = new WebSocket(`${protocol}//${window.location.host}/ws/stream`);

            socket.onopen = () => {
                const led = document.getElementById('systemLed');
                if (led) { led.className = 'w-2 h-2 rounded-full bg-emerald-500 animate-pulse'; }
                document.getElementById('engineStatusText').innerText = 'Telemetry Connected';
            };

            socket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                handleEvent(data);
            };

            socket.onclose = () => {
                const led = document.getElementById('systemLed');
                if (led) { led.className = 'w-2 h-2 rounded-full bg-rose-500'; }
                document.getElementById('engineStatusText').innerText = 'Reconnecting...';
                setTimeout(connectWS, 2000);
            };
        }

        function handleEvent(e) {
            // Agent updates
            if (e.universe) {
                const u = e.universe;
                const card = document.getElementById(`card-${u}`);
                const actionElem = document.getElementById(`action-${u}`);
                const badgeElem = document.getElementById(`badge-${u}`);
                const priceElem = document.getElementById(`price-${u}`);
                const stepElem = document.getElementById(`step-${u}`);
                const urlElem = document.getElementById(`url-${u}`);

                if (actionElem) actionElem.innerText = e.action;
                if (stepElem && e.step) stepElem.innerText = `Step ${String(e.step).padStart(2, '0')}/15`;
                if (urlElem && e.target_url) urlElem.innerText = e.target_url.replace('http://localhost:8000', 'mock:/');

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

                if (priceElem && e.found_price) {
                    priceElem.innerText = `₹${e.found_price.toLocaleString('en-IN')}`;
                    priceElem.classList.remove('text-slate-400');
                    priceElem.classList.add('text-slate-900');
                }

                if (e.status === 'discovery' || e.status === 'flagged') {
                    addBlackboardEntry(e.universe, e.status, e.action);
                }
            }

            if (e.type === 'COUPON_DISCOVERED') {
                addBlackboardEntry(e.universe, 'discovery', `Voucher extracted: ${e.code} (${e.discount_text}) on ${e.site}`);
            }
            if (e.type === 'DARK_PATTERN_FLAGGED') {
                addBlackboardEntry(e.universe, 'flagged', `${e.pattern_type}: ${e.details}`);
            }
            if (e.type === 'JUDGE_EVALUATING') {
                const dot = document.getElementById('judgeDot');
                if (dot) dot.className = 'w-2.5 h-2.5 rounded-full bg-blue-600 animate-ping';
                document.getElementById('verdictStatus').innerText = 'JUDGE SYNTHESIZING...';
                document.getElementById('verdictStatus').className = 'text-[11px] font-mono text-blue-600 font-bold';
            }
            if (e.type === 'VERDICT_FINALIZED') {
                renderVerdict(e.verdict);
            }
        }

        function addBlackboardEntry(universe, type, text) {
            const feed = document.getElementById('blackboardFeed');
            const placeholder = feed.querySelector('.italic');
            if (placeholder) placeholder.remove();

            const item = document.createElement('div');
            const now = new Date().toTimeString().split(' ')[0] + '.' + String(new Date().getMilliseconds()).padStart(3, '0');
            
            const isFlag = type === 'flagged';
            const borderCol = isFlag ? 'border-rose-200 bg-rose-50/60 text-rose-900' : 'border-amber-200 bg-amber-50/60 text-amber-900';
            const tag = isFlag ? 'DRIP_ALERT' : 'VOUCHER_SYNC';
            const tagStyle = isFlag ? 'bg-rose-100 text-rose-700 border-rose-300' : 'bg-amber-100 text-amber-700 border-amber-300';

            item.className = `p-2.5 rounded-xl border ${borderCol} flex items-start space-x-2 transition-all duration-300 shadow-sm`;
            item.innerHTML = `
                <span class="text-slate-400 select-none text-[10px] font-mono">${now}</span>
                <span class="px-1.5 py-0.2 rounded text-[9px] font-semibold border ${tagStyle}">${tag}</span>
                <span class="flex-1 text-slate-800 text-[11px] font-medium leading-relaxed">${text}</span>
            `;
            feed.prepend(item);
        }

        function renderVerdict(v) {
            const dot = document.getElementById('judgeDot');
            if (dot) dot.className = 'w-2.5 h-2.5 rounded-full bg-emerald-500';
            document.getElementById('verdictStatus').innerText = 'VERDICT FINALIZED';
            document.getElementById('verdictStatus').className = 'text-[11px] font-mono text-emerald-600 font-bold';

            const w = v.winner;
            let html = `
                <div class="bg-white border border-slate-200 rounded-xl p-5 space-y-4 font-mono shadow-sm">
                    <div class="flex items-center justify-between border-b border-slate-100 pb-3.5">
                        <div>
                            <span class="text-[10px] text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200 font-bold uppercase tracking-wider">Recommendation Consensus</span>
                            <div class="text-base font-sans font-bold text-slate-900 mt-1">${w.product_name}</div>
                            <div class="text-[11px] text-slate-500 font-medium font-sans">Merchant: <span class="text-slate-900 font-bold">${w.recommended_store}</span> via ${w.winning_universe}</div>
                        </div>
                        <div class="text-right">
                            <div class="text-[10px] text-slate-400 uppercase font-semibold">Confidence</div>
                            <div class="text-base font-bold text-emerald-600">${Math.round(w.confidence_score * 100)}%</div>
                        </div>
                    </div>

                    <!-- Cost Reconciliation Ledger -->
                    <div class="grid grid-cols-3 gap-2 py-1 text-center font-mono">
                        <div class="p-2.5 bg-slate-50 rounded-xl border border-slate-200/80">
                            <div class="text-[10px] text-slate-400 font-semibold">Surface Listed</div>
                            <div class="text-xs font-bold text-slate-700 mt-0.5">₹${w.naive_listed_cost.toLocaleString('en-IN')}</div>
                        </div>
                        <div class="p-2.5 bg-amber-50/70 rounded-xl border border-amber-200/80">
                            <div class="text-[10px] text-amber-600 font-semibold">Voucher Offset</div>
                            <div class="text-xs font-bold text-amber-700 mt-0.5">${w.coupon_applied}</div>
                        </div>
                        <div class="p-2.5 bg-emerald-50 rounded-xl border border-emerald-200">
                            <div class="text-[10px] text-emerald-600 font-semibold">True Landed Cost</div>
                            <div class="text-xs font-bold text-emerald-700 mt-0.5">₹${w.true_landed_cost.toLocaleString('en-IN')}</div>
                        </div>
                    </div>

                    <div class="p-3 rounded-xl bg-emerald-50/80 border border-emerald-200 flex items-center justify-between text-xs font-sans">
                        <span class="text-emerald-900 font-semibold">Verified net savings vs surface baseline:</span>
                        <span class="font-mono font-bold text-emerald-700 text-sm">Save ₹${w.savings_vs_first_result}</span>
                    </div>

                    <!-- Dark Patterns Neutralized -->
                    <div class="pt-1">
                        <div class="text-[10px] text-slate-400 uppercase tracking-wider mb-2 font-bold font-mono">Dark Patterns Neutralized</div>
                        <div class="space-y-2">
            `;

            v.dark_patterns_avoided.forEach(dp => {
                html += `
                    <div class="p-2.5 bg-rose-50/60 border border-rose-200/80 rounded-xl flex items-center justify-between text-[11px] font-sans">
                        <span class="text-rose-800 font-semibold font-mono">✕ ${dp.store}: ${dp.pattern}</span>
                        <span class="text-rose-600 text-[11px] font-medium">${dp.impact}</span>
                    </div>
                `;
            });

            html += `</div></div></div>`;

            document.getElementById('verdictContent').innerHTML = html;
            document.getElementById('verdictAudioBox').classList.remove('hidden');
            document.getElementById('verdictAudioText').innerText = v.spoken_summary;

            // Reset launch button
            document.getElementById('btnLaunch').disabled = false;
            document.getElementById('btnLaunchText').innerText = 'EXECUTE SWARM';
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
                    <div class="font-medium">Parallel browser workers executing across target endpoints...</div>
                </div>
            `;
            document.getElementById('verdictStatus').innerText = 'SWARM ACTIVE';
            document.getElementById('verdictStatus').className = 'text-[11px] font-mono text-blue-600 font-bold';
            
            document.getElementById('btnLaunch').disabled = true;
            document.getElementById('btnLaunchText').innerText = 'RUNNING...';

            if (socket && socket.readyState === WebSocket.OPEN) {
                socket.send(JSON.stringify({
                    action: 'start_race',
                    query: query
                }));
            }
        }

        window.onload = connectWS;
    </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content)
