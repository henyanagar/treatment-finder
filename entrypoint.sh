#!/usr/bin/env sh
set -e

pip install --no-cache-dir -r requirements.txt
python -m app.init_db
uvicorn app.main:app --host 0.0.0.0 --port 8000
