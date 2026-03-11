#!/usr/bin/env bash

docker compose -f docker-compose.e2e.yaml down -v 

colima stop

pkill node
echo -e "All stopped"
