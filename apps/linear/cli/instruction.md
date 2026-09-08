The `linear` CLI ([schpet/linear-cli](https://github.com/schpet/linear-cli)) is installed and authenticated via the LINEAR_API_KEY env var. Use it for Linear operations in the task above (`linear team list --json`, `linear issue query --team <KEY> --json`, `linear issue view <ID> --json`, ...; `linear <cmd> --help` for flags).

Do NOT use the Linear MCP server or direct `https://api.linear.app` calls. If the `linear` CLI cannot accomplish the task, stop and say so rather than escaping to other tools.
