FROM node:20-slim AS web-build

WORKDIR /app/guardpilot/apps/web
COPY guardpilot/apps/web/package*.json ./
RUN npm ci
COPY guardpilot/apps/web/ ./
COPY guardpilot/samples /app/guardpilot/samples
ARG VITE_API_BASE_URL=
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
RUN npm run build

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    GUARDPILOT_DB_PATH=/app/guardpilot/guardpilot.db \
    GUARDPILOT_LOG_DIR=/app/guardpilot/samples/outputs

WORKDIR /app
COPY guardpilot/apps/api ./guardpilot/apps/api
COPY guardpilot/samples ./guardpilot/samples
COPY guardpilot/reports ./guardpilot/reports
COPY --from=web-build /app/guardpilot/apps/web/dist ./guardpilot/apps/web/dist

RUN pip install --no-cache-dir -e ./guardpilot/apps/api

EXPOSE 8000
CMD ["sh", "-c", "uvicorn guardpilot.main:app --app-dir guardpilot/apps/api --host 0.0.0.0 --port ${PORT:-8000}"]
