from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from guardpilot.api.routes_bitget import router as bitget_router
from guardpilot.api.routes_health import router as health_router
from guardpilot.api.routes_intents import router as intents_router
from guardpilot.api.routes_logs import router as logs_router
from guardpilot.api.routes_replay import router as replay_router
from guardpilot.api.routes_reports import router as reports_router
from guardpilot.api.routes_trades import router as trades_router

app = FastAPI(
    title="GuardPilot API",
    description="Risk gateway and paper trading sandbox for autonomous trading agents",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(intents_router)
app.include_router(agents_router)
app.include_router(trades_router)
app.include_router(reports_router)
app.include_router(logs_router)
app.include_router(replay_router)
