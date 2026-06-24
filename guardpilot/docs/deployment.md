# Deployment

GuardPilot can be deployed in two ways.

## Full demo deployment

Use Render, Railway, Fly.io, or any Docker-compatible host.

The repository includes:

- `Dockerfile`
- `render.yaml`

The Docker service serves both:

- Dashboard: `/`
- API: `/api/v1/*`
- Health check: `/health`

Render setup:

1. Create a new Blueprint from the GitHub repository.
2. Select `render.yaml`.
3. Keep the health check path as `/health`.
4. Deploy.

No private Bitget key is required. The default demo uses committed sample data and paper-only replay evidence.

## Static frontend deployment

Use Vercel or Netlify if the API is already deployed somewhere else.

The repository includes:

- `vercel.json`
- `netlify.toml`

Set this environment variable in Vercel or Netlify:

```bash
VITE_API_BASE_URL=https://your-api-domain.example.com
```

If `VITE_API_BASE_URL` is empty, the production frontend calls the same origin. That works for the Docker full demo deployment.

## Local public preview

For a temporary review link from a local machine:

```bash
VITE_API_BASE_URL= npm --prefix guardpilot/apps/web run build
PYTHONPATH=guardpilot/apps/api python -m uvicorn guardpilot.main:app --app-dir guardpilot/apps/api --host 127.0.0.1 --port 8010
npx --yes localtunnel --port 8010 --subdomain guardpilot-bitget-demo
```

The localtunnel link is temporary and should not be treated as a permanent submission URL.
