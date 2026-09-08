A credential leak has been reported for the scraper fleet. Our incident response process is documented in Notion; start there and follow it:

1. Find which tracker issue the process tells you to run the audit from, and locate that issue in Linear.
2. Find the environment variable that halts the whole fleet, per the runbook the process points to.

Write a JSON file to `/app/result.json` with exactly these two keys:
```json
{
  "issue_title": "<the exact title of the Linear issue>",
  "halt_env_var": "<the environment variable name>"
}
```
