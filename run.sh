#!/bin/bash

cd "$(dirname "$0")"

python3 -m pip install -r requirements.txt --quiet

echo "starting frame2mental..."

python3 -m streamlit run app.py