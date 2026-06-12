# Railway Project Inventory

Discovered June 11, 2026 via `railway list --json`.
**Both old projects were deleted on June 11, 2026** at Elias's instruction — they were pre-existing and needed replacement.

## Account

- **Email:** primary.lamseyah@gmail.com
- **Workspace ID:** `4a2d2282-9e65-4eb5-af5a-5e93f65e2403`
- **Workspace name:** `lamseyahelias's Projects`

## Active Projects

### jarvis-cloud (ACTIVE — current)
- **Project ID:** `9311ab1b-de1d-4dd4-b691-6f50e7893a45`
- **Environment:** production (ID: `ab2820ce-bad4-47b2-8a62-a50be28956bd`)
- **Created:** 2026-06-11T21:18:08
- **Repo:** `LamseyahElias/jarvis-cloud-v2` (GitHub, main branch)
- **Services:**

| Service | ID | URL | Status |
|---------|-----|-----|--------|
| `api-server` | `9f67a4b3-3043-4772-b6fa-25c8cd11a105` | https://api-server-production-9980.up.railway.app | ✅ DEPLOYED |
| `telegram-bot` | `bad242ad-a297-4c9f-969a-b3c6772a2d69` | https://telegram-bot-production-c330.up.railway.app | ✅ DEPLOYED (needs TELEGRAM_TOKEN) |
| `belditalk-worker` | `b7459f3b-1c72-4013-bd6d-da45e9e8f5bb` | (cron, 10AM daily) | ✅ DEPLOYED (needs FB_PAGE_TOKEN) |

- **Deploy method:** Standalone directories with Dockerfile (Approach A)
- **api-server healthcheck:** `/api/health` — returns 200 with 8 agents, 0 tasks, "operational"
- **Notes:** Built from scratch after deleting old projects. Monorepo with 3 services. Dockerfile pattern required because Railpack can't handle monorepo subdirectories.
- **Env vars set:** DEEPSEEK_API_KEY (api-server only)
- **Env vars needed:** TELEGRAM_TOKEN (telegram-bot), FB_PAGE_TOKEN (belditalk-worker)

## Deleted Projects (history reference)

### enthusiastic-youth (DELETED 2026-06-11)
- **Project ID:** `d0817507-ba8c-4284-8b6a-aaef01d1389c`
- **Service:** `jarvis-cloud` (ID: `db738731-d999-4a95-8463-e93f5bf18c73`)
- **Environment:** production (ID: `56277675-9d80-4283-ad43-cd46544ae66f`)
- **Created:** 2026-05-29
- **Repo:** `LamseyahElias/jarvis-cloud` (also archived, now private)
- **Notes:** Was an attempt to deploy Hermes agent to Railway. 13+ deployment attempts, 1 successful (Python 3.13, RAILPACK build). Had env vars: DEEPSEEK_API_KEY, TELEGRAM_TOKEN, TELEGRAM_ALLOWED_USERS.

### cheerful-essence (DELETED 2026-06-11)
- **Project ID:** `ef0f0b4c-7d3b-4ae6-9c04-cd840991650e`
- **Service:** `web` (ID: `2cac5727-ccd3-4547-be56-b3d0a895cc49`)
- **Environment:** production (ID: `5fb7dc7c-b01c-4b20-9e15-734b30bc14b3`)
- **Created:** 2026-05-29
- **Notes:** No successful deployments. Created same day as enthusiastic-youth.
