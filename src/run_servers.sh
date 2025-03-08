#!/bin/bash

HOST_IP=$(hostname -I | awk '{print $1}')
PORT=5701
MAP_PORT=$PORT
echo "HOST_IP: $HOST_IP"

docker rm -f $(docker ps -a -q) -v
docker network rm hazelcast-network


docker network create hazelcast-network

for i in {1..3}
do

    docker run \
        -d\
        -v "$(pwd)"/hazelcast.yaml:/opt/hazelcast/hazelcast.yaml \
        --network hazelcast-network \
        -e HZ_NETWORK_PUBLICADDRESS=$HOST_IP:$MAP_PORT \
        -e HZ_CLUSTERNAME=hello-world \
        -e HAZELCAST_CONFIG=hazelcast.yaml \
        -p $MAP_PORT:$PORT hazelcast/hazelcast:5.3.8
    echo "Started Hazelcast member $i on port $MAP_PORT"
    MAP_PORT=$((MAP_PORT+1))
done

docker run \
    -d \
    --network hazelcast-network \
    -p 8080:8080 hazelcast/management-center:5.3
    

echo "Started Management Center at http://localhost:8080"