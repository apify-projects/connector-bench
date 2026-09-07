You have direct access to the GitHub REST API at `https://api.github.com`. The auth header is prepared in `/root/.api-headers/github`; use it for GitHub operations in the task above.

```
curl -sS -H @/root/.api-headers/github "https://api.github.com/repos/<owner>/<repo>/issues?per_page=10"
```

Do NOT use the `gh` CLI, the GitHub MCP server, or the `mcpc`/`mcporter`/`mcp-cli` bridges. If the REST API cannot accomplish the task, stop and say so rather than escaping to other tools.
