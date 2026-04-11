#!/usr/bin/env sh
set -e
# GROQ_API_KEY, GEMINI_API_KEY, and GROQ_MODEL are read from the process environment
# (set via docker-compose env_file / environment or your orchestrator).
python -m app.init_db
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
