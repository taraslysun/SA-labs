docker network create service-network \
&& docker build -t facade-service ./facade-service \
&& docker build -t logging-service ./logging-service \
&& docker build -t messages-service ./messages-service \
&& docker build -t config-server ./config-server \
&& docker run -d --name zookeeper-1 --network service-network -p 2181:2181 \
   -e ZOOKEEPER_CLIENT_PORT=2181 \
   -e ZOOKEEPER_TICK_TIME=2000 \
   confluentinc/cp-zookeeper:latest \
&& docker run -d --name kafka-1 --network service-network -p 9093:9093 \
   -e KAFKA_BROKER_ID=1 \
   -e KAFKA_ZOOKEEPER_CONNECT=zookeeper-1:2181 \
   -e KAFKA_ADVERTISED_LISTENERS="PLAINTEXT://kafka-1:9092,PLAINTEXT_HOST://localhost:9093" \
   -e KAFKA_LISTENER_SECURITY_PROTOCOL_MAP="PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT" \
   -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=3 \
   confluentinc/cp-kafka:latest \
&& docker run -d --name kafka-2 --network service-network -p 9094:9094 \
   -e KAFKA_BROKER_ID=2 \
   -e KAFKA_ZOOKEEPER_CONNECT=zookeeper-1:2181 \
   -e KAFKA_ADVERTISED_LISTENERS="PLAINTEXT://kafka-2:9092,PLAINTEXT_HOST://localhost:9094" \
   -e KAFKA_LISTENER_SECURITY_PROTOCOL_MAP="PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT" \
   -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=3 \
   confluentinc/cp-kafka:latest \
&& docker run -d --name kafka-3 --network service-network -p 9095:9095 \
   -e KAFKA_BROKER_ID=3 \
   -e KAFKA_ZOOKEEPER_CONNECT=zookeeper-1:2181 \
   -e KAFKA_ADVERTISED_LISTENERS="PLAINTEXT://kafka-3:9092,PLAINTEXT_HOST://localhost:9095" \
   -e KAFKA_LISTENER_SECURITY_PROTOCOL_MAP="PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT" \
   -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=3 \
   confluentinc/cp-kafka:latest

sleep 5

docker run -d --name facade-service --network service-network -p 8000:8000 facade-service:latest \
&& docker run -d --name logging-service-1 --network service-network -p 8001:8001 \
   -e HZ_PORT=5701 -e HZ_IP=10.10.229.253 \
   -v /var/run/docker.sock:/var/run/docker.sock \
   logging-service:latest \
&& docker run -d --name logging-service-2 --network service-network -p 8002:8001 \
   -e HZ_PORT=5702 -e HZ_IP=10.10.229.253 \
   -v /var/run/docker.sock:/var/run/docker.sock \
   logging-service:latest \
&& docker run -d --name logging-service-3 --network service-network -p 8003:8001 \
   -e HZ_PORT=5703 -e HZ_IP=10.10.229.253 \
   -v /var/run/docker.sock:/var/run/docker.sock \
   logging-service:latest \
&& docker run -d --name messages-service-1 --network service-network -p 8005:8005 \
   --link kafka-1 --link kafka-2 --link kafka-3 --link zookeeper-1 \
   messages-service:latest \
&& docker run -d --name messages-service-2 --network service-network -p 8006:8005 \
   --link kafka-1 --link kafka-2 --link kafka-3 --link zookeeper-1 \
   messages-service:latest \
&& docker run -d --name config-server --network service-network -p 8008:8008 config-server:latest
