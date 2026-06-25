# Deployment

GuardPilot can be deployed in two ways.

## Full demo deployment on Render

Use Render Blueprint from the GitHub repository.

The repository includes:

- `render.yaml`
- committed frontend build files under `guardpilot/apps/web/dist/`

The Render service uses the Python runtime and serves both:

- Dashboard: `/`
- API: `/api/v1/*`
- Health check: `/health`

Render setup:

1. Create a new Blueprint from the GitHub repository.
2. Select `render.yaml`.
3. Keep the health check path as `/health`.
4. Deploy the latest commit.

No private Bitget key is required. The default demo uses committed sample data and paper-only replay evidence.

The frontend is already built and committed so Render does not need to run npm during deploy. If the frontend changes, rebuild locally before pushing:

```bash
VITE_API_BASE_URL= npm --prefix guardpilot/apps/web run build
```

Render build command:

```bash
python -m pip install -e guardpilot/apps/api
```

Render start command:

```bash
uvicorn guardpilot.main:app --app-dir guardpilot/apps/api --host 0.0.0.0 --port $PORT
```

## Docker deployment

Use `Dockerfile` for Docker-compatible hosts such as Railway or Fly.io. The Docker image builds the frontend and serves it through the FastAPI app.

## Static frontend deployment

Use Vercel or Netlify if the API is already deployed somewhere else.

The repository includes:

- `vercel.json`
- `netlify.toml`

Set this environment variable in Vercel or Netlify:

```bash
VITE_API_BASE_URL=https://your-api-domain.example.com
```

If `VITE_API_BASE_URL` is empty, the production frontend calls the same origin. That works for the Render full demo deployment.

## Local public preview

For a temporary review link from a local machine:

```bash
VITE_API_BASE_URL= npm --prefix guardpilot/apps/web run build
PYTHONPATH=guardpilot/apps/api python -m uvicorn guardpilot.main:app --app-dir guardpilot/apps/api --host 127.0.0.1 --port 8010
npx --yes localtunnel --port 8010 --subdomain guardpilot-bitget-demo
```

The localtunnel link is temporary and should not be treated as a permanent submission URL.
