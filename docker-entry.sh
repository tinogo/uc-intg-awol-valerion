#!/bin/bash
# Docker entrypoint script

cd /usr/src/app
uv sync --locked --no-dev
uv run --no-sync python -m uc_intg_awol_valerion