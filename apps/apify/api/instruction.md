You have direct access to the Apify REST API at `https://api.apify.com/v2`. The auth header is prepared in `/root/.api-headers/apify`; use it for Apify operations in the task above.

```
curl -sS -H @/root/.api-headers/apify "https://api.apify.com/v2/acts?limit=10"
```

Do NOT use the `apify` CLI, the Apify MCP server, or the `mcpc`/`mcporter`/`mcp-cli` bridges. If the REST API cannot accomplish the task, stop and say so rather than escaping to other tools.
