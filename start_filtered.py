"""Wrapper that strips disabled tools before serving (stateless HTTP)."""
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
    print("[filter] No DISABLED_TOOLS env var set", file=sys.stderr, flush=True)

if __name__ == "__main__":
    mcp_server.settings.host = "0.0.0.0"
    mcp_server.settings.port = 8080
    # Stateless mode = no session required (matches the previous behavior)
    mcp_server.settings.stateless_http = True
    asyncio.run(mcp_server.run_streamable_http_async())
