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
    title="Multiverse Browser API",
    description="Backend swarm orchestrator and mock ecommerce testbed for Multiverse Browser (wHACKiest 2026 - Track 2)",
    version=settings.VERSION
)

# Enable CORS for external frontend
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
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "mode": "read_only_guarded"
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
            "message": "Connected to Multiverse Browser Realtime Stream"
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
                # Run asynchronously in background task
                asyncio.create_task(orchestrator.execute_run(query, target_urls))
                
    except WebSocketDisconnect:
        if websocket in connected_websockets:
            connected_websockets.remove(websocket)

@app.get("/", response_class=HTMLResponse)
async def live_dashboard():
    """
    Built-in live interactive board for immediate testing and presentation demo.
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Multiverse Browser · Swarm Race Dashboard</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            @keyframes pulse-ring { 0% { transform: scale(0.95); opacity: 0.8; } 50% { transform: scale(1.05); opacity: 0.4; } 100% { transform: scale(0.95); opacity: 0.8; } }
            .telepathy-pulse { animation: pulse-ring 2s infinite ease-in-out; }
        </style>
    </head>
    <body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col font-sans">
        <!-- Top Nav -->
        <header class="border-b border-slate-800 bg-slate-900/60 backdrop-blur px-6 py-4 flex items-center justify-between sticky top-0 z-50">
            <div class="flex items-center space-x-3">
                <div class="w-8 h-8 rounded-lg bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center font-bold text-lg">🌌</div>
                <div>
                    <h1 class="font-bold text-lg tracking-tight bg-gradient-to-r from-indigo-200 via-sky-300 to-white bg-clip-text text-transparent">Multiverse Browser</h1>
                    <p class="text-xs text-slate-400">wHACKiest 2026 · Track 2 (Beyond the Browser)</p>
                </div>
            </div>
            <div class="flex items-center space-x-4 text-xs">
                <span class="inline-flex items-center px-2.5 py-1 rounded-full bg-emerald-950/80 text-emerald-400 border border-emerald-800/60">
                    <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-2 animate-ping"></span> Live Swarm Engine
                </span>
                <a href="/mock" target="_blank" class="text-indigo-400 hover:text-indigo-300 font-medium">🛒 Inspect Mock Shops →</a>
            </div>
        </header>

        <!-- Main Body -->
        <main class="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">
            <!-- Goal Query Bar -->
            <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl">
                <div class="flex flex-col md:flex-row gap-3">
                    <div class="relative flex-1">
                        <span class="absolute inset-y-0 left-0 flex items-center pl-4 text-slate-400">🎙️</span>
                        <input id="goalInput" type="text" value="Find wireless ANC headphones under ₹3,000" class="w-full pl-11 pr-4 py-3 bg-slate-950 border border-slate-700 rounded-xl text-sm focus:outline-none focus:border-indigo-500 text-white placeholder-slate-500 font-medium">
                    </div>
                    <button id="btnLaunch" onclick="startMultiverseRace()" class="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold rounded-xl text-sm transition shadow-lg shadow-indigo-500/20 flex items-center justify-center gap-2">
                        <span>🚀 Launch Parallel Universes</span>
                    </button>
                </div>
                <div class="mt-3 flex items-center justify-between text-xs text-slate-400">
                    <span>Guardrails: 🛡️ Read-Only Mode · Domain Allowlist · Step Budget (15)</span>
                    <span id="connectionStatus" class="text-amber-400">Connecting to stream...</span>
                </div>
            </div>

            <!-- 4 Parallel Universes Grid -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <!-- Universe 1 -->
                <div id="card-budget" class="bg-slate-900/80 border border-slate-800 rounded-xl p-4 flex flex-col justify-between transition-all duration-300">
                    <div>
                        <div class="flex items-center justify-between mb-3">
                            <span class="text-xs font-bold px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800">UNIVERSE 1</span>
                            <span id="badge-budget" class="text-xs text-slate-400">Idle</span>
                        </div>
                        <h3 class="font-bold text-slate-100 flex items-center gap-2">💰 Budget Universe</h3>
                        <p class="text-xs text-slate-400 mt-1">Hunts lowest total landed checkout cost.</p>
                        
                        <div class="mt-4 p-3 bg-slate-950 rounded-lg border border-slate-800/80 min-h-[90px]">
                            <div class="text-[11px] text-slate-400">Current Action:</div>
                            <div id="action-budget" class="text-xs text-slate-300 mt-1 font-mono">Awaiting launch...</div>
                        </div>
                    </div>
                    <div class="mt-4 pt-3 border-t border-slate-800 flex justify-between items-baseline">
                        <span class="text-xs text-slate-400">Landed Price:</span>
                        <span id="price-budget" class="text-lg font-bold text-emerald-400">--</span>
                    </div>
                </div>

                <!-- Universe 2 -->
                <div id="card-deal_hunter" class="bg-slate-900/80 border border-slate-800 rounded-xl p-4 flex flex-col justify-between transition-all duration-300">
                    <div>
                        <div class="flex items-center justify-between mb-3">
                            <span class="text-xs font-bold px-2 py-0.5 rounded bg-amber-950 text-amber-400 border border-amber-800">UNIVERSE 2</span>
                            <span id="badge-deal_hunter" class="text-xs text-slate-400">Idle</span>
                        </div>
                        <h3 class="font-bold text-slate-100 flex items-center gap-2">🎟️ Deal Hunter</h3>
                        <p class="text-xs text-slate-400 mt-1">Scans hidden vouchers, promo codes & sales.</p>
                        
                        <div class="mt-4 p-3 bg-slate-950 rounded-lg border border-slate-800/80 min-h-[90px]">
                            <div class="text-[11px] text-slate-400">Current Action:</div>
                            <div id="action-deal_hunter" class="text-xs text-slate-300 mt-1 font-mono">Awaiting launch...</div>
                        </div>
                    </div>
                    <div class="mt-4 pt-3 border-t border-slate-800 flex justify-between items-baseline">
                        <span class="text-xs text-slate-400">Voucher Value:</span>
                        <span id="price-deal_hunter" class="text-lg font-bold text-amber-400">--</span>
                    </div>
                </div>

                <!-- Universe 3 -->
                <div id="card-trust" class="bg-slate-900/80 border border-slate-800 rounded-xl p-4 flex flex-col justify-between transition-all duration-300">
                    <div>
                        <div class="flex items-center justify-between mb-3">
                            <span class="text-xs font-bold px-2 py-0.5 rounded bg-blue-950 text-blue-400 border border-blue-800">UNIVERSE 3</span>
                            <span id="badge-trust" class="text-xs text-slate-400">Idle</span>
                        </div>
                        <h3 class="font-bold text-slate-100 flex items-center gap-2">🛡️ Trust & Signals</h3>
                        <p class="text-xs text-slate-400 mt-1">Flags fake MRPs & audits manufacturer warranties.</p>
                        
                        <div class="mt-4 p-3 bg-slate-950 rounded-lg border border-slate-800/80 min-h-[90px]">
                            <div class="text-[11px] text-slate-400">Current Action:</div>
                            <div id="action-trust" class="text-xs text-slate-300 mt-1 font-mono">Awaiting launch...</div>
                        </div>
                    </div>
                    <div class="mt-4 pt-3 border-t border-slate-800 flex justify-between items-baseline">
                        <span class="text-xs text-slate-400">Warranty / MRP:</span>
                        <span id="price-trust" class="text-lg font-bold text-blue-400">--</span>
                    </div>
                </div>

                <!-- Universe 4 -->
                <div id="card-value" class="bg-slate-900/80 border border-slate-800 rounded-xl p-4 flex flex-col justify-between transition-all duration-300">
                    <div>
                        <div class="flex items-center justify-between mb-3">
                            <span class="text-xs font-bold px-2 py-0.5 rounded bg-purple-950 text-purple-400 border border-purple-800">UNIVERSE 4</span>
                            <span id="badge-value" class="text-xs text-slate-400">Idle</span>
                        </div>
                        <h3 class="font-bold text-slate-100 flex items-center gap-2">⭐ Best Value</h3>
                        <p class="text-xs text-slate-400 mt-1">Balances ANC specs, battery life & ratings.</p>
                        
                        <div class="mt-4 p-3 bg-slate-950 rounded-lg border border-slate-800/80 min-h-[90px]">
                            <div class="text-[11px] text-slate-400">Current Action:</div>
                            <div id="action-value" class="text-xs text-slate-300 mt-1 font-mono">Awaiting launch...</div>
                        </div>
                    </div>
                    <div class="mt-4 pt-3 border-t border-slate-800 flex justify-between items-baseline">
                        <span class="text-xs text-slate-400">Score Matrix:</span>
                        <span id="price-value" class="text-lg font-bold text-purple-400">--</span>
                    </div>
                </div>
            </div>

            <!-- Blackboard Feed & Final Verdict -->
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <!-- Shared Blackboard Activity -->
                <div class="lg:col-span-1 bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col h-80">
                    <div class="flex items-center justify-between pb-2 border-b border-slate-800">
                        <h3 class="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                            <span>📡 Shared Blackboard Telepathy</span>
                        </h3>
                        <span class="text-[10px] bg-indigo-950 text-indigo-300 px-2 py-0.5 rounded">Cross-Agent Memory</span>
                    </div>
                    <div id="blackboardFeed" class="flex-1 overflow-y-auto space-y-2 mt-3 pr-1 text-xs">
                        <div class="text-slate-500 italic">No discoveries posted yet. Launch the swarm to watch cross-agent discovery.</div>
                    </div>
                </div>

                <!-- Final Judge Verdict -->
                <div class="lg:col-span-2 bg-gradient-to-br from-slate-900 via-indigo-950/20 to-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col justify-between">
                    <div>
                        <div class="flex items-center justify-between pb-2 border-b border-slate-800">
                            <h3 class="font-bold text-sm text-indigo-300 flex items-center gap-2">
                                <span>⚖️ Multiverse Judge Verdict</span>
                                <span class="text-[10px] bg-purple-950 text-purple-300 px-2 py-0.5 rounded border border-purple-800/50">AWS Bedrock + ElevenLabs</span>
                            </h3>
                            <span id="verdictStatus" class="text-xs text-slate-400">Waiting for swarm convergence</span>
                        </div>

                        <div id="verdictContent" class="mt-4 text-sm text-slate-300 space-y-3">
                            <p class="text-slate-400">When the 4 universes finish their race, the Judge merges the screenshot evidence, calculates the true landed cost vs the naive listing, and flags dark patterns avoided.</p>
                        </div>
                    </div>

                    <div id="verdictAudioBox" class="mt-4 pt-3 border-t border-slate-800 hidden flex items-center justify-between">
                        <div class="flex items-center gap-2 text-xs text-emerald-400 font-medium">
                            <span>🔊 Spoken Verdict (ElevenLabs):</span>
                            <span id="verdictAudioText" class="text-slate-300 truncate max-w-md"></span>
                        </div>
                        <button onclick="playSampleAudio()" class="px-3 py-1 bg-emerald-600 hover:bg-emerald-500 text-xs font-bold rounded text-white">▶ Play Verdict</button>
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
                    document.getElementById('connectionStatus').innerText = '🟢 Connected to Engine';
                    document.getElementById('connectionStatus').className = 'text-emerald-400';
                };

                socket.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    handleEvent(data);
                };

                socket.onclose = () => {
                    document.getElementById('connectionStatus').innerText = '🔴 Disconnected. Retrying...';
                    document.getElementById('connectionStatus').className = 'text-red-400';
                    setTimeout(connectWS, 2000);
                };
            }

            function handleEvent(e) {
                // Agent step updates
                if (e.universe) {
                    const u = e.universe;
                    const actionElem = document.getElementById(`action-${u}`);
                    const badgeElem = document.getElementById(`badge-${u}`);
                    const priceElem = document.getElementById(`price-${u}`);

                    if (actionElem) actionElem.innerText = e.action;
                    if (badgeElem) badgeElem.innerText = e.status.toUpperCase();
                    if (priceElem && e.found_price) priceElem.innerText = `₹${e.found_price}`;

                    if (e.status === 'discovery' || e.status === 'flagged') {
                        addBlackboardItem(e.action, e.status);
                    }
                }

                if (e.type === 'COUPON_DISCOVERED') {
                    addBlackboardItem(`🎟️ [${e.universe}] Found coupon '${e.code}' (${e.discount_text}) on ${e.site}`, 'discovery');
                }
                if (e.type === 'DARK_PATTERN_FLAGGED') {
                    addBlackboardItem(`🚨 [${e.universe}] ${e.pattern_type}: ${e.details}`, 'flagged');
                }
                if (e.type === 'VERDICT_FINALIZED') {
                    renderVerdict(e.verdict);
                }
            }

            function addBlackboardItem(text, type) {
                const feed = document.getElementById('blackboardFeed');
                const item = document.createElement('div');
                const borderClass = type === 'flagged' ? 'border-red-500/50 bg-red-950/20 text-red-200' : 'border-indigo-500/50 bg-indigo-950/20 text-indigo-200';
                item.className = `p-2 rounded border ${borderClass} font-mono text-[11px]`;
                item.innerText = text;
                feed.prepend(item);
            }

            function renderVerdict(v) {
                document.getElementById('verdictStatus').innerText = '✅ Consensus Reached';
                document.getElementById('verdictStatus').className = 'text-xs text-emerald-400 font-bold';
                
                const w = v.winner;
                let html = `
                    <div class="p-3 bg-emerald-950/30 border border-emerald-800/60 rounded-xl space-y-2">
                        <div class="flex justify-between items-center">
                            <span class="text-xs font-semibold text-emerald-400 uppercase tracking-wide">🏆 Winner Recommendation</span>
                            <span class="text-xs bg-emerald-900/60 text-emerald-200 px-2 py-0.5 rounded">Confidence: ${Math.round(w.confidence_score * 100)}%</span>
                        </div>
                        <div class="text-lg font-bold text-white">${w.product_name} on <span class="text-indigo-400">${w.recommended_store}</span></div>
                        <div class="flex gap-4 text-xs">
                            <div>True Landed Cost: <strong class="text-emerald-400 text-sm">₹${w.true_landed_cost}</strong></div>
                            <div>Saved vs First Result: <strong class="text-emerald-400 text-sm">₹${w.savings_vs_first_result}</strong></div>
                            <div>Coupon: <strong class="text-amber-400">${w.coupon_applied}</strong></div>
                        </div>
                    </div>

                    <div class="space-y-1">
                        <div class="text-xs font-bold text-slate-300">🛡️ Dark Patterns Bypassed:</div>
                `;
                
                v.dark_patterns_avoided.forEach(dp => {
                    html += `
                        <div class="text-xs p-2 bg-slate-950 rounded border border-slate-800 flex justify-between">
                            <span class="text-red-400 font-medium">⚠️ ${dp.store}: ${dp.pattern}</span>
                            <span class="text-slate-400">${dp.impact}</span>
                        </div>
                    `;
                });
                html += `</div>`;

                document.getElementById('verdictContent').innerHTML = html;
                document.getElementById('verdictAudioBox').classList.remove('hidden');
                document.getElementById('verdictAudioText').innerText = v.spoken_summary;
            }

            function playSampleAudio() {
                const u = new SpeechSynthesisUtterance(document.getElementById('verdictAudioText').innerText);
                window.speechSynthesis.speak(u);
            }

            function startMultiverseRace() {
                const query = document.getElementById('goalInput').value;
                document.getElementById('blackboardFeed').innerHTML = '';
                document.getElementById('verdictContent').innerHTML = '<p class="text-indigo-300 animate-pulse">Universes exploring target web endpoints... streaming live evidence.</p>';
                document.getElementById('verdictStatus').innerText = 'RACE IN PROGRESS...';
                document.getElementById('verdictStatus').className = 'text-xs text-amber-400 font-bold';
                
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
