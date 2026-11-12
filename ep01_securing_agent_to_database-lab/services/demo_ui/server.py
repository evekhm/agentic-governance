"""FastAPI Governance Workbench backend (Live SSE + Static Trace Replay)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

STATIC_DIR = Path(__file__).resolve().parent / "static"
TRACES_DIR = Path(__file__).resolve().parents[2] / "recorded_traces"

app = FastAPI(title="Episode 01 Governance Workbench")
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    html_path = STATIC_DIR / "index.html"
    return HTMLResponse(html_path.read_text(encoding="utf-8"))


@app.get("/api/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "ep01-workbench"}


@app.get("/api/replay/{threat_id}")
async def replay_bundle(threat_id: str) -> list[dict]:
    path = TRACES_DIR / f"{threat_id.lower()}.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


@app.get("/api/stream/{threat_id}")
async def stream_trace(threat_id: str) -> StreamingResponse:
    events = await replay_bundle(threat_id)

    async def _gen() -> AsyncGenerator[str, None]:
        for ev in events:
            yield f"data: {json.dumps(ev)}\n\n"

    return StreamingResponse(_gen(), media_type="text/event-stream")
