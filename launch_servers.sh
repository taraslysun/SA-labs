#!/bin/bash
set -e

HOST_IP=$(hostname -I | awk '{print $1}')
echo "Using host IP: $HOST_IP"


if ! docker network ls | grep -q "hazelcast-network"; then
  docker network create hazelcast-network
fi


docker build -t facade-service ./facade-service
docker run -d --name facade-service \
  --network hazelcast-network \
  -p 8000:8000 \
  facade-service

docker build -t logging-service-1 ./logging-service
docker run -d --name logging-service-1 \
  --network hazelcast-network \
  -p 8001:8001 \
  -e HZ_PORT=5701 -e HZ_IP="$HOST_IP" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  logging-service-1


docker build -t logging-service-2 ./logging-service
docker run -d --name logging-service-2 \
  --network hazelcast-network \
  -p 8002:8001 \
  -e HZ_PORT=5702 -e HZ_IP="$HOST_IP" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  logging-service-2


docker build -t logging-service-3 ./logging-service
docker run -d --name logging-service-3 \
  --network hazelcast-network \
  -p 8003:8001 \
  -e HZ_PORT=5703 -e HZ_IP="$HOST_IP" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  logging-service-3


docker build -t messages-service ./messages-service
docker run -d --name messages-service \
  --network hazelcast-network \
  -p 8007:8007 \
  messages-service


docker build -t config-server ./config-server
docker run -d --name config-server \
  --network hazelcast-network \
  -p 8008:8008 \
  config-server

echo "All containers launched."
