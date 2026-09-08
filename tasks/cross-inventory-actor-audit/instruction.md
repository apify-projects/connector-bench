Our "Scraper Inventory" page in Notion notes that one scraper is built on a public Apify Store Actor.

1. Find that scraper and the Actor it references in the inventory.
2. Look up the Actor on the Apify platform.
3. Write a JSON file to `/app/result.json` with exactly these three keys:
   ```json
   {
     "scraper": "<the scraper's name>",
     "actor_full_name": "<username/name of the Actor>",
     "actor_id": "<the Actor's opaque ID string>"
   }
   ```

Write the values exactly as returned by the API, with no extra whitespace or formatting.
