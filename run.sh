#!/usr/bin/env bash

# Exit immediately if a command fails
set -e

# Check if argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <virtual_env_dir>"
  exit 1
fi

VENV_DIR=$1

colima stop

echo -e "Running colima"
colima start

# echo -e "Building containers"
# docker compose -f docker-compose.e2e.yaml down -v 
# docker compose -f docker-compose.e2e.yaml build
docker compose -f docker-compose.e2e.yaml up -d

#sleep 10

# Activate the virtual environment passed as argument
source "./$VENV_DIR/bin/activate"

echo -e "Running the back-end"
cd app/
nohup python main.py &

sleep 10
deactivate

echo -e "Running the front-end"
cd ./client/
nohup npm run dev &