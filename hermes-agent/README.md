# JARVIS Cloud — Hermes Agent
# This directory contains the Docker deployment for the full Hermes AI agent
# on Railway. It uses Dockerfile build with:
#   - hermes-agent 0.14.0 from PyPI
#   - Builtin skills (84) auto-initialized at startup
#   - Entrypoint script to generate config from Railway env vars
#
# To add custom skills, run after deployment:
#   hermes skills install <skill-name>
