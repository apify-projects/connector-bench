The `mcporter` CLI is installed and already configured with the GitHub MCP server as `github`. Use it for GitHub operations in the task above.

```
mcporter list github
mcporter call github.<tool-name> arg=value
mcporter call github.<tool-name> --args '{"arg": "value"}'
mcporter --help
```

Do NOT use the `gh` CLI, the GitHub MCP server directly, or `curl`/direct GitHub API calls. If `mcporter` cannot accomplish the task, stop and say so rather than escaping to other tools.
