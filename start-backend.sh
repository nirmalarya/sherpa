#!/bin/bash
# Start backend server
venv/bin/uvicorn sherpa.api.main:app --reload --port 8000 --host 0.0.0.0
