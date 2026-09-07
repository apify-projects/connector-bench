The `mcp-cli` CLI is installed and already configured with the Notion MCP server as `notion` (config in `/app/server_config.json`; run it from `/app`). Use it for Notion operations in the task above.

```
mcp-cli tools --server notion
mcp-cli tools --server notion --all
mcp-cli cmd --server notion --tool <tool-name> --tool-args '{"arg": "value"}' --raw
mcp-cli --help
```

Do NOT use the `ntn` CLI, the Notion MCP server directly, or direct `https://api.notion.com` calls. If `mcp-cli` cannot accomplish the task, stop and say so rather than escaping to other tools.
