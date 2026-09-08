The `mcpc` CLI is installed and already connected to Linear as `@linear`. Use it for Linear operations in the task above.

```
mcpc @linear tools-list
mcpc @linear tools-get <tool-name>
mcpc --json @linear tools-call <tool-name> arg:=value
mcpc --help
```

Do NOT use the `linear` CLI, the Linear MCP server directly, or direct `https://api.linear.app` calls. If `mcpc` cannot accomplish the task, stop and say so rather than escaping to other tools.
