You have direct access to the Notion REST API at `https://api.notion.com/v1`. The auth headers (token + Notion-Version) are prepared in `/root/.api-headers/notion`; use them for Notion operations in the task above.

```
curl -sS -H @/root/.api-headers/notion -X POST "https://api.notion.com/v1/search" -H 'Content-Type: application/json' -d '{"query":"..."}'
curl -sS -H @/root/.api-headers/notion "https://api.notion.com/v1/blocks/<page-id>/children"
```

Do NOT use the `ntn` CLI, the Notion MCP server, or the `mcpc`/`mcporter`/`mcp-cli` bridges. If the REST API cannot accomplish the task, stop and say so rather than escaping to other tools.
