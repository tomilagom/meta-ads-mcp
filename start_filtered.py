"""Wrapper that strips disabled tools before serving."""
import os
import sys
import asyncio

# Lista de tools a deshabilitar vía env var, separadas por coma
disabled_raw = os.getenv("DISABLED_TOOLS", "")
disabled = {t.strip() for t in disabled_raw.split(",") if t.strip()}

# Importar el servidor MCP (esto registra todas las tools)
from meta_ads_mcp.core.server import mcp_server

if disabled:
    # FastMCP guarda las tools en _tool_manager._tools (dict por nombre)
    tm = mcp_server._tool_manager
    removed = []
    for name in list(tm._tools.keys()):
        if name in disabled:
            del tm._tools[name]
            removed.append(name)
    print(f"[filter] Disabled {len(removed)} tools: {', '.join(removed)}", file=sys.stderr, flush=True)
else:
    print("[filter] No DISABLED_TOOLS env var set, all tools enabled", file=sys.stderr, flush=True)

# Arrancar el server en HTTP
if __name__ == "__main__":
    asyncio.run(
        mcp_server.run_streamable_http_async(
            host="0.0.0.0",
            port=8080,
        )
    )
