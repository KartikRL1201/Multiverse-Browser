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
    High-performance engineering dashboard for Multiverse Browser.
    Designed with Linear/Raycast minimalist dark aesthetics, real-time telemetry,
    authentic browser session frames, and live blackboard synchronization.
    """
    html_content = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multiverse Browser · Swarm Control</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700&family=Geist+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['Geist', '-apple-system', 'BlinkMacSystemFont', 'system-ui', 'sans-serif'],
                        mono: ['"Geist Mono"', 'ui-monospace', 'monospace']
                    },
                    colors: {
                        obsidian: '#090A0E',
                        panel: '#101218',
                        surface: '#151821',
                        borderSubtle: '#1E222D',
                        borderHover: '#2A3040',
                        accentBlue: '#2563EB',
                        accentEmerald: '#10B981',
                        accentAmber: '#F59E0B',
                        accentRose: '#F43F5E'
                    }
                }
            }
        }
    </script>
    <style>
        body {
            background-color: #090A0E;
            color: #E2E8F0;
            background-image: radial-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 0);
            background-size: 24px 24px;
        }
        
        .scanline {
            position: relative;
            overflow: hidden;
        }
        .scanline::after {
            content: " ";
            display: block;
            position: absolute;
            top: 0; left: 0; bottom: 0; right: 0;
            background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.03), rgba(0, 255, 0, 0.01), rgba(0, 0, 255, 0.03));
            z-index: 20;
            background-size: 100% 2px, 3px 100%;
            pointer-events: none;
            opacity: 0.3;
        }

        @keyframes radarSweep {
            0% { transform: translateY(-100%); }
            100% { transform: translateY(300%); }
        }
        .radar-active {
            position: relative;
            overflow: hidden;
        }
        .radar-active::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; height: 40px;
            background: linear-gradient(180deg, transparent, rgba(59, 130, 246, 0.15), transparent);
            animation: radarSweep 2.2s infinite ease-in-out;
            pointer-events: none;
        }

        /* Waveform visualizer */
        @keyframes soundWave {
            0%, 100% { height: 4px; }
            50% { height: 18px; }
        }
        .wave-bar {
            width: 3px;
            background-color: #10B981;
            border-radius: 9999px;
            animation: soundWave 1.2s infinite ease-in-out;
        }
        .wave-bar:nth-child(2) { animation-delay: 0.15s; }
        .wave-bar:nth-child(3) { animation-delay: 0.3s; }
        .wave-bar:nth-child(4) { animation-delay: 0.45s; }
        .wave-bar:nth-child(5) { animation-delay: 0.2s; }
        .wave-bar:nth-child(6) { animation-delay: 0.4s; }

        /* Custom scrollbar */
        ::-webkit-scrollbar { width: 5px; height: 5px; }
        ::-webkit-scrollbar-track { background: #090A0E; }
        ::-webkit-scrollbar-thumb { background: #1E222D; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #2A3040; }
    </style>
</head>
<body class="min-h-screen flex flex-col font-sans antialiased text-slate-200 selection:bg-blue-600/30 selection:text-blue-200">

    <!-- Top Command Navigation -->
    <header class="border-b border-[#1A1E29] bg-[#0C0E14]/80 backdrop-blur-md px-6 py-3 sticky top-0 z-50">
        <div class="max-w-7xl mx-auto flex items-center justify-between">
            <div class="flex items-center space-x-3.5">
                <div class="w-8 h-8 rounded-md bg-[#161A24] border border-[#232938] flex items-center justify-center font-mono font-semibold text-xs text-blue-400">
                    M // B
                </div>
                <div>
                    <div class="flex items-center space-x-2">
                        <span class="text-sm font-semibold tracking-tight text-white">Multiverse Browser</span>
                        <span class="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-blue-950/60 text-blue-400 border border-blue-900/60 font-medium">v0.1.0-mvp</span>
                    </div>
                    <p class="text-[11px] text-slate-400 font-mono">wHACKiest 2026 · Track 2 (Beyond the Browser)</p>
                </div>
            </div>

            <!-- System Metrics & Telemetry Status -->
            <div class="flex items-center space-x-4">
                <div class="flex items-center space-x-2 text-[11px] font-mono px-3 py-1.5 rounded-md bg-[#12151D] border border-[#1E2330]">
                    <span id="systemLed" class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                    <span id="engineStatusText" class="text-slate-300">Swarm Engine Ready</span>
                </div>
                <a href="/mock" target="_blank" class="text-[11px] font-mono text-slate-400 hover:text-white px-3 py-1.5 rounded-md bg-[#12151D] border border-[#1E2330] hover:border-slate-600 transition flex items-center gap-1.5">
                    <span>Inspect Seed Shops</span>
                    <svg class="w-3 h-3 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
                </a>
            </div>
        </div>
    </header>

    <!-- Main Workspace -->
    <main class="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">

        <!-- Command Input / Intent Specification -->
        <div class="bg-[#10131B] border border-[#1A1F2B] rounded-xl p-4 shadow-2xl relative">
            <div class="flex flex-col sm:flex-row gap-3">
                <div class="relative flex-1">
                    <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
                    </div>
                    <input id="goalInput" type="text" value="Find wireless ANC headphones under ₹3,000" class="w-full pl-10 pr-4 py-2.5 bg-[#090B10] border border-[#1E2433] rounded-lg text-sm font-sans focus:outline-none focus:border-blue-500/80 text-white placeholder-slate-600 transition">
                </div>
                <button id="btnLaunch" onclick="startMultiverseRace()" class="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 active:bg-blue-700 text-white font-medium rounded-lg text-xs font-mono tracking-wide transition shadow-sm flex items-center justify-center gap-2">
                    <svg id="launchIcon" class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                    <span id="btnLaunchText">EXECUTE SWARM</span>
                </button>
            </div>
            
            <!-- Guardrails Metadata Pill Bar -->
            <div class="mt-3 pt-3 border-t border-[#171B26] flex flex-wrap items-center justify-between text-[11px] font-mono text-slate-400">
                <div class="flex items-center space-x-3">
                    <span class="text-slate-500">Guardrails:</span>
                    <span class="inline-flex items-center gap-1 text-slate-300">
                        <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span> Read-Only Enforced
                    </span>
                    <span class="text-slate-600">·</span>
                    <span class="text-slate-300">Allowlist: 3 Domains</span>
                    <span class="text-slate-600">·</span>
                    <span class="text-slate-300">Step Budget: 15 / Worker</span>
                </div>
                <div id="targetUrlCounter" class="text-slate-500">
                    Endpoints: 3 Seed Stores Active
                </div>
            </div>
        </div>

        <!-- 4 Parallel Browser Universes Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            
            <!-- Universe 1: Budget / True Cost -->
            <div id="card-budget" class="bg-[#10131B] border border-[#1A1F2B] hover:border-[#2A3142] rounded-xl flex flex-col justify-between transition-all duration-300 overflow-hidden">
                <div>
                    <!-- Browser Window Chrome -->
                    <div class="px-3.5 py-2.5 border-b border-[#181D28] bg-[#0C0F15] flex items-center justify-between">
                        <div class="flex items-center space-x-1.5">
                            <span class="w-2 h-2 rounded-full bg-slate-700"></span>
                            <span class="w-2 h-2 rounded-full bg-slate-700"></span>
                            <span class="w-2 h-2 rounded-full bg-slate-700"></span>
                            <span class="ml-2 text-[10px] font-mono uppercase tracking-wider text-slate-400 font-semibold">Universe 01</span>
                        </div>
                        <span id="badge-budget" class="text-[9px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">IDLE</span>
                    </div>

                    <!-- Inner Card Header -->
                    <div class="p-3.5">
                        <div class="flex items-baseline justify-between">
                            <h3 class="text-xs font-semibold text-white tracking-tight">Landed Cost Auditor</h3>
                            <span class="text-[10px] font-mono text-slate-400" id="step-budget">Step --/15</span>
                        </div>
                        <p class="text-[11px] text-slate-400 mt-0.5">Navigates to checkout to detect drip fees.</p>

                        <!-- Simulated Address Bar -->
                        <div class="mt-2.5 px-2 py-1 bg-[#090B10] rounded border border-[#181C26] text-[10px] font-mono text-slate-400 truncate" id="url-budget">
                            mock://awaiting-session
                        </div>

                        <!-- Live Action Terminal -->
                        <div class="mt-3 p-2.5 bg-[#090B10] rounded-lg border border-[#181C26] min-h-[85px] flex flex-col justify-between">
                            <div class="text-[10px] font-mono text-slate-500">DOM Activity:</div>
                            <div id="action-budget" class="text-[11px] font-mono text-slate-300 mt-1 line-clamp-3">
                                Standby for query execution...
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Footer Metric -->
                <div class="p-3.5 border-t border-[#181D28] bg-[#0D1017] flex justify-between items-baseline">
                    <span class="text-[11px] font-mono text-slate-400">True Landed Cost:</span>
                    <span id="price-budget" class="text-base font-mono font-bold text-slate-400">--</span>
                </div>
            </div>

            <!-- Universe 2: Deal Hunter -->
            <div id="card-deal_hunter" class="bg-[#10131B] border border-[#1A1F2B] hover:border-[#2A3142] rounded-xl flex flex-col justify-between transition-all duration-300 overflow-hidden">
                <div>
                    <!-- Browser Window Chrome -->
                    <div class="px-3.5 py-2.5 border-b border-[#181D28] bg-[#0C0F15] flex items-center justify-between">
                        <div class="flex items-center space-x-1.5">
                            <span class="w-2 h-2 rounded-full bg-slate-700"></span>
                            <span class="w-2 h-2 rounded-full bg-slate-700"></span>
                            <span class="w-2 h-2 rounded-full bg-slate-700"></span>
                            <span class="ml-2 text-[10px] font-mono uppercase tracking-wider text-slate-400 font-semibold">Universe 02</span>
                        </div>
                        <span id="badge-deal_hunter" class="text-[9px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">IDLE</span>
                    </div>

                    <!-- Inner Card Header -->
                    <div class="p-3.5">
                        <div class="flex items-baseline justify-between">
                            <h3 class="text-xs font-semibold text-white tracking-tight">Voucher & Code Scraper</h3>
                            <span class="text-[10px] font-mono text-slate-400" id="step-deal_hunter">Step --/15</span>
                        </div>
                        <p class="text-[11px] text-slate-400 mt-0.5">Scrapes promotional banners and hidden footers.</p>

                        <!-- Simulated Address Bar -->
                        <div class="mt-2.5 px-2 py-1 bg-[#090B10] rounded border border-[#181C26] text-[10px] font-mono text-slate-400 truncate" id="url-deal_hunter">
                            mock://awaiting-session
                        </div>

                        <!-- Live Action Terminal -->
                        <div class="mt-3 p-2.5 bg-[#090B10] rounded-lg border border-[#181C26] min-h-[85px] flex flex-col justify-between">
                            <div class="text-[10px] font-mono text-slate-500">DOM Activity:</div>
                            <div id="action-deal_hunter" class="text-[11px] font-mono text-slate-300 mt-1 line-clamp-3">
                                Standby for query execution...
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Footer Metric -->
                <div class="p-3.5 border-t border-[#181D28] bg-[#0D1017] flex justify-between items-baseline">
                    <span class="text-[11px] font-mono text-slate-400">Extracted Voucher:</span>
                    <span id="price-deal_hunter" class="text-base font-mono font-bold text-slate-400">--</span>
                </div>
            </div>

            <!-- Universe 3: Trust & Signals -->
            <div id="card-trust" class="bg-[#10131B] border border-[#1A1F2B] hover:border-[#2A3142] rounded-xl flex flex-col justify-between transition-all duration-300 overflow-hidden">
                <div>
                    <!-- Browser Window Chrome -->
                    <div class="px-3.5 py-2.5 border-b border-[#181D28] bg-[#0C0F15] flex items-center justify-between">
                        <div class="flex items-center space-x-1.5">
                            <span class="w-2 h-2 rounded-full bg-slate-700"></span>
                            <span class="w-2 h-2 rounded-full bg-slate-700"></span>
                            <span class="w-2 h-2 rounded-full bg-slate-700"></span>
                            <span class="ml-2 text-[10px] font-mono uppercase tracking-wider text-slate-400 font-semibold">Universe 03</span>
                        </div>
                        <span id="badge-trust" class="text-[9px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">IDLE</span>
                    </div>

                    <!-- Inner Card Header -->
                    <div class="p-3.5">
                        <div class="flex items-baseline justify-between">
                            <h3 class="text-xs font-semibold text-white tracking-tight">Authenticity Auditor</h3>
                            <span class="text-[10px] font-mono text-slate-400" id="step-trust">Step --/15</span>
                        </div>
                        <p class="text-[11px] text-slate-400 mt-0.5">Audits warranties and flags deceptive MRP claims.</p>

                        <!-- Simulated Address Bar -->
                        <div class="mt-2.5 px-2 py-1 bg-[#090B10] rounded border border-[#181C26] text-[10px] font-mono text-slate-400 truncate" id="url-trust">
                            mock://awaiting-session
                        </div>

                        <!-- Live Action Terminal -->
                        <div class="mt-3 p-2.5 bg-[#090B10] rounded-lg border border-[#181C26] min-h-[85px] flex flex-col justify-between">
                            <div class="text-[10px] font-mono text-slate-500">DOM Activity:</div>
                            <div id="action-trust" class="text-[11px] font-mono text-slate-300 mt-1 line-clamp-3">
                                Standby for query execution...
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Footer Metric -->
                <div class="p-3.5 border-t border-[#181D28] bg-[#0D1017] flex justify-between items-baseline">
                    <span class="text-[11px] font-mono text-slate-400">Trust Index:</span>
                    <span id="price-trust" class="text-base font-mono font-bold text-slate-400">--</span>
                </div>
            </div>

            <!-- Universe 4: Best Value -->
            <div id="card-value" class="bg-[#10131B] border border-[#1A1F2B] hover:border-[#2A3142] rounded-xl flex flex-col justify-between transition-all duration-300 overflow-hidden">
                <div>
                    <!-- Browser Window Chrome -->
                    <div class="px-3.5 py-2.5 border-b border-[#181D28] bg-[#0C0F15] flex items-center justify-between">
                        <div class="flex items-center space-x-1.5">
                            <span class="w-2 h-2 rounded-full bg-slate-700"></span>
                            <span class="w-2 h-2 rounded-full bg-slate-700"></span>
                            <span class="w-2 h-2 rounded-full bg-slate-700"></span>
                            <span class="ml-2 text-[10px] font-mono uppercase tracking-wider text-slate-400 font-semibold">Universe 04</span>
                        </div>
                        <span id="badge-value" class="text-[9px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">IDLE</span>
                    </div>

                    <!-- Inner Card Header -->
                    <div class="p-3.5">
                        <div class="flex items-baseline justify-between">
                            <h3 class="text-xs font-semibold text-white tracking-tight">Feature / Cost Matrix</h3>
                            <span class="text-[10px] font-mono text-slate-400" id="step-value">Step --/15</span>
                        </div>
                        <p class="text-[11px] text-slate-400 mt-0.5">Calculates ANC specs, battery & sentiment trade-offs.</p>

                        <!-- Simulated Address Bar -->
                        <div class="mt-2.5 px-2 py-1 bg-[#090B10] rounded border border-[#181C26] text-[10px] font-mono text-slate-400 truncate" id="url-value">
                            mock://awaiting-session
                        </div>

                        <!-- Live Action Terminal -->
                        <div class="mt-3 p-2.5 bg-[#090B10] rounded-lg border border-[#181C26] min-h-[85px] flex flex-col justify-between">
                            <div class="text-[10px] font-mono text-slate-500">DOM Activity:</div>
                            <div id="action-value" class="text-[11px] font-mono text-slate-300 mt-1 line-clamp-3">
                                Standby for query execution...
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Footer Metric -->
                <div class="p-3.5 border-t border-[#181D28] bg-[#0D1017] flex justify-between items-baseline">
                    <span class="text-[11px] font-mono text-slate-400">Value Rating:</span>
                    <span id="price-value" class="text-base font-mono font-bold text-slate-400">--</span>
                </div>
            </div>
        </div>

        <!-- Lower Section: Shared Intelligence Bus & Final Synthesized Ledger -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">
            
            <!-- Left: Shared State Bus (Blackboard) -->
            <div class="lg:col-span-5 bg-[#10131B] border border-[#1A1F2B] rounded-xl p-4 flex flex-col h-[340px]">
                <div class="flex items-center justify-between pb-3 border-b border-[#181D28]">
                    <div class="flex items-center space-x-2">
                        <span class="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
                        <h3 class="text-xs font-semibold text-white tracking-tight font-mono uppercase">Shared Blackboard Bus</h3>
                    </div>
                    <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-[#171B26] text-slate-400 border border-[#232838]">CROSS-AGENT MEMORY</span>
                </div>

                <!-- Realtime Feed -->
                <div id="blackboardFeed" class="flex-1 overflow-y-auto space-y-2 mt-3 pr-1 text-[11px] font-mono">
                    <div class="text-slate-600 italic py-8 text-center">
                        Shared state channel idle. Launch swarm to observe cross-agent discovery exchange.
                    </div>
                </div>
            </div>

            <!-- Right: Synthesized Verdict & Financial Reconciliation -->
            <div class="lg:col-span-7 bg-[#10131B] border border-[#1A1F2B] rounded-xl p-5 flex flex-col justify-between min-h-[340px]">
                <div>
                    <div class="flex items-center justify-between pb-3 border-b border-[#181D28]">
                        <div class="flex items-center space-x-2.5">
                            <span class="w-2 h-2 rounded-full bg-slate-500" id="judgeDot"></span>
                            <h3 class="text-xs font-semibold text-white tracking-tight font-mono uppercase">Multiverse Judge Synthesis</h3>
                            <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-950/40 text-blue-400 border border-blue-900/40">AWS Bedrock + S3</span>
                        </div>
                        <span id="verdictStatus" class="text-[11px] font-mono text-slate-400">Awaiting Swarm Run</span>
                    </div>

                    <!-- Dynamic Verdict Card -->
                    <div id="verdictContent" class="mt-4">
                        <div class="p-6 rounded-lg border border-dashed border-[#1E2330] text-center text-slate-500 text-xs font-mono">
                            The central Bedrock Judge will aggregate DOM screenshot receipts, reconcile true landed costs against surface listings, and produce a verified recommendation ledger.
                        </div>
                    </div>
                </div>

                <!-- Spoken Verdict Playback Dock -->
                <div id="verdictAudioBox" class="mt-4 pt-3 border-t border-[#181D28] hidden flex items-center justify-between">
                    <div class="flex items-center space-x-3 text-xs">
                        <div class="flex items-center space-x-1 h-5 px-2 bg-emerald-950/50 border border-emerald-900/60 rounded">
                            <div class="wave-bar"></div>
                            <div class="wave-bar"></div>
                            <div class="wave-bar"></div>
                            <div class="wave-bar"></div>
                            <div class="wave-bar"></div>
                            <div class="wave-bar"></div>
                        </div>
                        <div class="font-mono text-[11px]">
                            <span class="text-emerald-400 font-medium">ElevenLabs TTS:</span>
                            <span id="verdictAudioText" class="text-slate-300 ml-1.5 truncate max-w-sm inline-block align-bottom"></span>
                        </div>
                    </div>
                    <button onclick="playSampleAudio()" class="px-3 py-1.5 bg-[#171B26] hover:bg-[#202534] border border-[#272D3E] text-slate-200 text-xs font-mono rounded transition flex items-center gap-1.5">
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
                        badgeElem.className = 'text-[9px] font-mono px-1.5 py-0.5 rounded bg-blue-950 text-blue-400 border border-blue-800';
                        if (card) card.classList.add('radar-active');
                    } else if (e.status === 'discovery') {
                        badgeElem.className = 'text-[9px] font-mono px-1.5 py-0.5 rounded bg-amber-950 text-amber-400 border border-amber-800';
                    } else if (e.status === 'flagged') {
                        badgeElem.className = 'text-[9px] font-mono px-1.5 py-0.5 rounded bg-rose-950 text-rose-400 border border-rose-800';
                    } else if (e.status === 'completed') {
                        badgeElem.className = 'text-[9px] font-mono px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800';
                        if (card) card.classList.remove('radar-active');
                    }
                }

                if (priceElem && e.found_price) {
                    priceElem.innerText = `₹${e.found_price.toLocaleString('en-IN')}`;
                    priceElem.classList.remove('text-slate-400');
                    priceElem.classList.add('text-white');
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
                if (dot) dot.className = 'w-2 h-2 rounded-full bg-blue-500 animate-ping';
                document.getElementById('verdictStatus').innerText = 'JUDGE SYNTHESIZING...';
                document.getElementById('verdictStatus').className = 'text-[11px] font-mono text-blue-400 font-semibold';
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
            const borderCol = isFlag ? 'border-rose-900/60 bg-rose-950/20 text-rose-300' : 'border-amber-900/60 bg-amber-950/20 text-amber-300';
            const tag = isFlag ? 'DRIP_ALERT' : 'VOUCHER_SYNC';

            item.className = `p-2 rounded border ${borderCol} flex items-start space-x-2 transition-all duration-300`;
            item.innerHTML = `
                <span class="text-slate-500 select-none">${now}</span>
                <span class="px-1 py-0.2 bg-[#12151D] border border-current rounded text-[9px] font-semibold">${tag}</span>
                <span class="flex-1 text-slate-200">${text}</span>
            `;
            feed.prepend(item);
        }

        function renderVerdict(v) {
            const dot = document.getElementById('judgeDot');
            if (dot) dot.className = 'w-2 h-2 rounded-full bg-emerald-500';
            document.getElementById('verdictStatus').innerText = 'VERDICT FINALIZED';
            document.getElementById('verdictStatus').className = 'text-[11px] font-mono text-emerald-400 font-semibold';

            const w = v.winner;
            let html = `
                <div class="bg-[#0C0F16] border border-[#1C2130] rounded-lg p-4 space-y-3 font-mono">
                    <div class="flex items-center justify-between border-b border-[#1A1F2D] pb-3">
                        <div>
                            <span class="text-[10px] text-emerald-400 font-semibold tracking-wider uppercase">Recommendation Consensus</span>
                            <div class="text-sm font-sans font-bold text-white mt-0.5">${w.product_name}</div>
                            <div class="text-[11px] text-slate-400">Merchant: <span class="text-slate-200 font-semibold">${w.recommended_store}</span> via ${w.winning_universe}</div>
                        </div>
                        <div class="text-right">
                            <div class="text-[10px] text-slate-500 uppercase">Confidence</div>
                            <div class="text-sm font-bold text-emerald-400">${Math.round(w.confidence_score * 100)}%</div>
                        </div>
                    </div>

                    <!-- Cost Reconciliation Ledger -->
                    <div class="grid grid-cols-3 gap-2 py-1 text-center">
                        <div class="p-2 bg-[#11141C] rounded border border-[#1A1F2C]">
                            <div class="text-[10px] text-slate-500">Surface Listed</div>
                            <div class="text-xs font-semibold text-slate-300 mt-0.5">₹${w.naive_listed_cost.toLocaleString('en-IN')}</div>
                        </div>
                        <div class="p-2 bg-[#11141C] rounded border border-[#1A1F2C]">
                            <div class="text-[10px] text-slate-500">Voucher Offset</div>
                            <div class="text-xs font-semibold text-amber-400 mt-0.5">${w.coupon_applied}</div>
                        </div>
                        <div class="p-2 bg-emerald-950/30 rounded border border-emerald-900/50">
                            <div class="text-[10px] text-emerald-400 font-medium">True Landed Cost</div>
                            <div class="text-xs font-bold text-emerald-300 mt-0.5">₹${w.true_landed_cost.toLocaleString('en-IN')}</div>
                        </div>
                    </div>

                    <div class="p-2.5 rounded bg-emerald-950/20 border border-emerald-900/40 flex items-center justify-between text-xs font-sans">
                        <span class="text-slate-300">Verified savings vs surface baseline:</span>
                        <span class="font-mono font-bold text-emerald-400">Save ₹${w.savings_vs_first_result}</span>
                    </div>

                    <!-- Dark Patterns Neutralized -->
                    <div class="pt-2">
                        <div class="text-[10px] text-slate-500 uppercase tracking-wider mb-1.5 font-semibold">Dark Patterns Neutralized</div>
                        <div class="space-y-1.5">
            `;

            v.dark_patterns_avoided.forEach(dp => {
                html += `
                    <div class="p-2 bg-[#0E1118] border border-[#1A1E2B] rounded flex items-center justify-between text-[11px]">
                        <span class="text-rose-400 font-medium">✕ ${dp.store}: ${dp.pattern}</span>
                        <span class="text-slate-400 text-[10px]">${dp.impact}</span>
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
                <div class="p-6 rounded-lg border border-blue-900/40 bg-blue-950/10 text-center text-blue-300 text-xs font-mono space-y-2">
                    <div class="inline-block w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                    <div>Parallel browser workers executing across target endpoints...</div>
                </div>
            `;
            document.getElementById('verdictStatus').innerText = 'SWARM ACTIVE';
            document.getElementById('verdictStatus').className = 'text-[11px] font-mono text-blue-400 font-semibold';
            
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
