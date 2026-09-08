Your task uses both Linear and GitHub:

1. In the Scraper Fleet team in Linear, find the issue whose description references an upstream GitHub pull request.
2. Follow the reference: look up that pull request on GitHub.
3. Write a JSON file to `/app/result.json` with exactly these four keys:
   ```json
   {
     "pr_number": <the PR number, as a JSON number>,
     "pr_title": "<the PR title>",
     "pr_author": "<the PR author's GitHub login>",
     "pr_merged": <true or false, as a JSON boolean>
   }
   ```

Write the title and login exactly as returned by the API, with no extra whitespace or formatting.
