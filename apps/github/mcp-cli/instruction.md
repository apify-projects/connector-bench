The `mcp-cli` CLI is installed and already configured with the GitHub MCP server as `github` (config in `/app/server_config.json`; run it from `/app`). Use it for GitHub operations in the task above.

```
mcp-cli tools --server github
mcp-cli tools --server github --all
mcp-cli cmd --server github --tool <tool-name> --tool-args '{"arg": "value"}' --raw
mcp-cli --help
```

Do NOT use the `gh` CLI, the GitHub MCP server directly, or `curl`/direct GitHub API calls. If `mcp-cli` cannot accomplish the task, stop and say so rather than escaping to other tools.
