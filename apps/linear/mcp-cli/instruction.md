The `mcp-cli` CLI is installed and already configured with the Linear MCP server as `linear` (config in `/app/server_config.json`; run it from `/app`). Use it for Linear operations in the task above.

```
mcp-cli tools --server linear
mcp-cli tools --server linear --all
mcp-cli cmd --server linear --tool <tool-name> --tool-args '{"arg": "value"}' --raw
mcp-cli --help
```

Do NOT use the `linear` CLI, the Linear MCP server directly, or direct `https://api.linear.app` calls. If `mcp-cli` cannot accomplish the task, stop and say so rather than escaping to other tools.
