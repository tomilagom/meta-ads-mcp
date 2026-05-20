"""Wrapper that strips disabled tools before serving (with header auth)."""
import os
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

disabled_raw = os.getenv("DISABLED_TOOLS", "")
disabled = {t.strip() for t in disabled_raw.split(",") if t.strip()}

from meta_ads_mcp.core.server import mcp_server

# Ensure all tool modules are imported (so they register their tools)
from meta_ads_mcp.core import (
    accounts, campaigns, adsets, ads, insights, authentication,
    ads_library, budget_schedules, reports, openai_deep_research,
)

# Filter out disabled tools
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

# Configure HTTP settings
mcp_server.settings.host = "0.0.0.0"
mcp_server.settings.port = 8080
mcp_server.settings.stateless_http = True
mcp_server.settings.json_response = True

# FastMCP's __init__ auto-enables DNS-rebinding protection with a localhost-only
# allowlist whenever the default host (127.0.0.1) is used. Reassigning
# `settings.host` above does not re-evaluate that; the allowlist stays
# localhost-only, so requests with the public Host header get 421
# "Invalid Host header". Disable the guard since auth is handled by the
# X-META-ACCESS-TOKEN header and TLS by the reverse proxy.
from mcp.server.transport_security import TransportSecuritySettings
mcp_server.settings.transport_security = TransportSecuritySettings(
    enable_dns_rebinding_protection=False,
)

# CRITICAL: setup the auth middleware that reads X-META-ACCESS-TOKEN header
try:
    from meta_ads_mcp.core.http_auth_integration import setup_fastmcp_http_auth
    setup_fastmcp_http_auth(mcp_server)
    print("[auth] HTTP authentication middleware enabled", file=sys.stderr, flush=True)
except Exception as e:
    print(f"[auth] WARNING: failed to setup HTTP auth middleware: {e}", file=sys.stderr, flush=True)

# Start the server using the same method pipeboard uses
if __name__ == "__main__":
    mcp_server.run(transport="streamable-http")
