# 01: Project skeleton and deploy spike

**What to build:** A running, deployed empty system the whole team can build on. A backend and a frontend start locally, a real Postgres runs in local Docker with schema migrations, the test runner works against it, and a trivial page and health check are reachable on a public URL. The first deploy also runs the Hyperdrive spike: one Cloudflare Worker doing a `BEGIN; SELECT ... FOR UPDATE; COMMIT` through Hyperdrive, to decide where the backend lives.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] Backend and frontend run locally with one documented command each
- [ ] A local Docker Postgres runs, and the same migrations apply to Docker and to Supabase
- [ ] A first test calls a health endpoint through the API test client against the Docker database, is seen failing, then passes
- [ ] Each test rolls back its database changes so tests stay independent
- [ ] `.env` is ignored by git and no secret key is committed or exposed in the frontend
- [ ] A public URL shows the frontend and answers the health check, and it opens on a phone outside the team's network
- [ ] The Hyperdrive transaction spike result is recorded: either backend on Cloudflare, or the agreed Render/Fly fallback is chosen and used
