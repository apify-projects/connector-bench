The `mcporter` CLI is installed and already configured with the Notion MCP server as `notion`. Use it for Notion operations in the task above.

```
mcporter list notion
mcporter call notion.<tool-name> arg=value
mcporter call notion.<tool-name> --args '{"arg": "value"}'
mcporter --help
```

Do NOT use the `ntn` CLI, the Notion MCP server directly, or direct `https://api.notion.com` calls. If `mcporter` cannot accomplish the task, stop and say so rather than escaping to other tools.
