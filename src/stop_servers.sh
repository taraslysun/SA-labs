#!/bin/bash

docker rm -f $(docker ps -a -q) -v

docker network rm hazelcast-network