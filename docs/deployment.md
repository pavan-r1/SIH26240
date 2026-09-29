# Local container deployment

Install Docker Desktop, copy `.env.example` to `.env`, set a private `POSTGRES_PASSWORD`, then run `docker compose up --build`. The database health check gates API startup; API seeds the development schema; the browser app is available at `http://localhost:3000`, API docs at `http://localhost:8000/docs`.

This is a local development stack, not a hardened production deployment. It has no authentication, TLS termination, backups, production secret management, rate limiting, or persistent photo storage. Do not expose it publicly.
