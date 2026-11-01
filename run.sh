#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
if [ -x .venv/bin/python ]; then
    APP_PYTHON=.venv/bin/python
elif [ -x venv/bin/python ]; then
    APP_PYTHON=venv/bin/python
else
    APP_PYTHON=python3
fi
exec "$APP_PYTHON" -m streamlit run app.py --server.address 127.0.0.1
