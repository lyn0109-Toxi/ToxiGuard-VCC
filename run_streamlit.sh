#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
python3 -m streamlit run app.py --server.port 8507
