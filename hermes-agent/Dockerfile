# JARVIS Cloud — Hermes Agent Dockerfile
# Deploys the full Hermes AI agent on Railway

FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install hermes-agent (pin to same version as local for compatibility)
RUN pip install --no-cache-dir hermes-agent==0.14.0

# Install telepresence so the agent can show presence / typing indicators
RUN pip install --no-cache-dir httpx

# Copy skills directory (13MB, 609 files — includes all categories)
COPY skills/ /app/skills/

# Copy entrypoint and config template
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

COPY config.template.yaml /app/config.template.yaml

# Create empty data directories (mounted at runtime)
RUN mkdir -p /app/data /app/cache /app/logs

# Railway passes $PORT dynamically
EXPOSE $PORT

ENTRYPOINT ["/app/entrypoint.sh"]
