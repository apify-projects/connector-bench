You have direct access to the Linear GraphQL API at `https://api.linear.app/graphql`. The auth header is prepared in `/root/.api-headers/linear`; use it for Linear operations in the task above.

```
curl -sS -X POST -H @/root/.api-headers/linear -H 'Content-Type: application/json' \
  -d '{"query":"{ teams { nodes { id key name } } }"}' https://api.linear.app/graphql
curl -sS -X POST -H @/root/.api-headers/linear -H 'Content-Type: application/json' \
  -d '{"query":"query($id: String!) { team(id: $id) { issues { nodes { identifier title } } } }","variables":{"id":"..."}}' https://api.linear.app/graphql
```

Do NOT use the `linear` CLI, the Linear MCP server, or the `mcpc`/`mcporter`/`mcp-cli` bridges. If the GraphQL API cannot accomplish the task, stop and say so rather than escaping to other tools.
