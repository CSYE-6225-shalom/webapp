#!/bin/bash

# Create a network
docker network create monitoring

# Stop and remove existing containers
docker stop graphite grafana 2>/dev/null
docker rm graphite grafana 2>/dev/null

# Start Graphite with network
docker run -d \
  --name graphite \
  --network monitoring \
  -p 80:80 \
  -p 8125:8125/udp \
  graphiteapp/graphite-statsd

# Start Grafana with network
docker run -d \
  --name grafana \
  --network monitoring \
  -p 3000:3000 \
  grafana/grafana

echo "Graphite and Grafana have been started successfully."
