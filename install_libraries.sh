#!/bin/bash

# Update package lists
sudo apt-get update

# Upgrade existing packages
sudo apt-get upgrade -y

# Install Python3 and pip if they are not installed
sudo apt-get install python3 python3-pip cmake libopenblas-dev -y

# Install necessary Python libraries
pip3 install cryptography requests jwt numpy pandas schedule

# Definícia cesty k priečinku s aplikáciou (upravte podľa vašich potrieb)
APP_DIR="/home/rdy/bitcoin-trader"

LOGS_DIR="$APP_DIR/logs"
CONFIG_DIR="$APP_DIR/config"

# Kontrola existencie adresára logs
if [ ! -d "$LOGS_DIR" ]; then
  echo "Vytváram adresár 'logs'..."
  mkdir -p "$LOGS_DIR"
  touch "$LOGS_DIR/application.log"
fi

# Kontrola existencie adresára config
if [ ! -d "$CONFIG_DIR" ]; then
  echo "Vytváram adresár 'config'..."
  mkdir -p "$CONFIG_DIR"
fi

# spustitelny run
chmod +x run.sh

echo "All necessary libraries have been installed."
