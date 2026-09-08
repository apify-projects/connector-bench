The `mcporter` CLI is installed and already configured with the Linear MCP server as `linear`. Use it for Linear operations in the task above.

```
mcporter list linear
mcporter call linear.<tool-name> arg=value
mcporter call linear.<tool-name> --args '{"arg": "value"}'
mcporter --help
```

Do NOT use the `linear` CLI, the Linear MCP server directly, or direct `https://api.linear.app` calls. If `mcporter` cannot accomplish the task, stop and say so rather than escaping to other tools.
