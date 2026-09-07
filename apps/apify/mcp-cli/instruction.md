The `mcp-cli` CLI is installed and already configured with the Apify MCP server as `apify` (config in `/app/server_config.json`; run it from `/app`). Use it for Apify operations in the task above.

```
mcp-cli tools --server apify
mcp-cli tools --server apify --all
mcp-cli cmd --server apify --tool <tool-name> --tool-args '{"arg": "value"}' --raw
mcp-cli --help
```

Do NOT use the `apify` CLI, the Apify MCP server directly, or direct `https://api.apify.com` calls. If `mcp-cli` cannot accomplish the task, stop and say so rather than escaping to other tools.
