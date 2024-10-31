#!/bin/bash

# Stop and remove existing containers
docker stop graphite grafana 2>/dev/null
docker rm graphite grafana 2>/dev/null

# Remove Graphite and Grafana images (optional)
docker rmi graphiteapp/graphite-statsd grafana/grafana 2>/dev/null

# Remove the network
docker network rm monitoring 2>/dev/null

echo "Tear down complete: Containers, images, and network have been removed."