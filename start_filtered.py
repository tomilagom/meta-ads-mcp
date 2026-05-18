"""Wrapper that strips disabled tools before serving."""
import os
import sys
import asyncio

disabled_raw = os.getenv("DISABLED_TOOLS", "")
disabled = {t.strip() for t in disabled_raw.split(",") if t.strip()}

from meta_ads_mcp.core.server import mcp_server

if disabled:
    tm = mcp_server._tool_manager
    removed = []
    for name in list(tm._tools.keys()):
        if name in disabled:
            del tm._tools[name]
            removed.append(name)
    print(f"[filter] Disabled {len(removed)} tools: {', '.join(removed)}", file=sys.stderr, flush=True)
else:
    print("[filter] No DISABLED_TOOLS env var set, all tools enabled", file=sys.stderr, flush=True)

if __name__ == "__main__":
    # Configure host/port via settings (FastMCP v1.x API)
    mcp_server.settings.host = "0.0.0.0"
    mcp_server.settings.port = 8080
    asyncio.run(mcp_server.run_streamable_http_async())
