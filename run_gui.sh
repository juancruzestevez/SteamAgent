#!/bin/bash
# Lanzador de SteamAgent Desktop
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"
source venv/bin/activate
python -m src.ui.app
