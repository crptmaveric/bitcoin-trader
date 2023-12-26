#!/bin/bash

# Nastavte cestu k vášmu projektu
PROJECT_PATH="/home/rdy/bitcoin-trader"

# Nastavenie PYTHONPATH pre tento skript
export PYTHONPATH="$PROJECT_PATH:$PYTHONPATH"

# Spustenie Python skriptu
python "$PROJECT_PATH/src/main.py"
