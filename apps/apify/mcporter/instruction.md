The `mcporter` CLI is installed and already configured with the Apify MCP server as `apify`. Use it for Apify operations in the task above.

```
mcporter list apify
mcporter call apify.<tool-name> arg=value
mcporter call apify.<tool-name> --args '{"arg": "value"}'
mcporter --help
```

Do NOT use the `apify` CLI, the Apify MCP server directly, or direct `https://api.apify.com` calls. If `mcporter` cannot accomplish the task, stop and say so rather than escaping to other tools.
