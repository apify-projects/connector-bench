The `mcpc` CLI is installed and already connected to Notion as `@notion`. Use it for Notion operations in the task above.

```
mcpc @notion tools-list
mcpc @notion tools-get <tool-name>
mcpc --json @notion tools-call <tool-name> arg:=value
mcpc --help
```

Do NOT use the `ntn` CLI, the Notion MCP server directly, or direct `https://api.notion.com` calls. If `mcpc` cannot accomplish the task, stop and say so rather than escaping to other tools.
