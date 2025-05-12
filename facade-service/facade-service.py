import fastapi
import requests
import uuid
from pydantic import BaseModel
import random
from confluent_kafka import Producer
from fastapi import FastAPI
from contextlib import asynccontextmanager
import os
import consul
from consul import Check
import time

CONSUL_HOST = os.getenv("CONSUL_HOST", "consul")
CONSUL_PORT = int(os.getenv("CONSUL_PORT", "8500"))
consul_client = consul.Consul(host=CONSUL_HOST, port=CONSUL_PORT)
SERVICE_NAME = os.getenv("SERVICE_NAME", "facade-service")
SERVICE_ID   = f"{SERVICE_NAME}-{os.getenv('HOSTNAME', '')}"
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8000"))

try:
    print(f"Attempting to connect to Consul at {CONSUL_HOST}:{CONSUL_PORT}")
    _, bs_data = consul_client.kv.get('mq/bootstrap_servers')
    if bs_data and bs_data['Value']:
        bootstrap = bs_data['Value'].decode()
        _, topic_data = consul_client.kv.get('mq/topic')
        topic = topic_data['Value'].decode()
        print(f"Successfully connected to Consul and retrieved KV data")
    else:
        print("Consul KV data not available yet")
except Exception as e:
    print(f"Error connecting to Consul: {e}")


producer = Producer({'bootstrap.servers': bootstrap, 'client.id': SERVICE_NAME})

app = FastAPI()

class Message(BaseModel):
    msg: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Registering service {SERVICE_NAME} with ID {SERVICE_ID} on {os.getenv('HOSTNAME', 'localhost')}:{SERVICE_PORT}")
    consul_client.agent.service.register(
        name=SERVICE_NAME,
        service_id=SERVICE_ID,
        address=os.getenv("HOSTNAME", "localhost"),
        port=SERVICE_PORT,
        check=Check.http(
            url=f"http://{os.getenv('HOSTNAME', 'localhost')}:{SERVICE_PORT}/health",
            interval="10s"
        )
    )
    try:
        yield
    finally:
        consul_client.agent.service.deregister(SERVICE_ID)
        print(f"Deregistered service {SERVICE_ID}")

app.router.lifespan_context = lifespan

@app.get("/health")
def health():
    return {"status": "healthy"}


def get_service_addresses(service_name: str) -> list:
    addresses = []
    
    try:
        _, nodes = consul_client.catalog.service(service_name)
        print(f"Service {service_name} nodes: {nodes}")
        addresses = [
            f"http://{node['ServiceAddress']}:{node['ServicePort']}"
            for node in nodes
            if node['ServiceAddress']
        ]
        print(f"Found {len(addresses)} addresses for {service_name}: {addresses}")
    except Exception as e:
        print(f"Error discovering service {service_name}: {e}")
            
    return addresses


def get_service_data(addresses: list, path: str = "", first_random=False) -> dict:
    if not addresses:
        return {"error": "No service addresses available"}
        
    random.shuffle(addresses)
    result = []
    for service_addr in addresses:
        try:
            endpoint = f"{service_addr}{path}"
            print(f"Trying to connect to: {endpoint}")
            response = requests.get(endpoint, timeout=3)
            if response.status_code == 200:
                response_data = response.json()
                if first_random:
                    return response_data.get("data", {})
                result.append(response_data.get("data", {}))
        except Exception as e:
            print(f"Exception accessing {service_addr}: {e}")
    
    if result:
        return result
    else:
        return {"error": "Could not connect to service"}


@app.get("/", status_code=200)
def get_facade():
    messages_addresses = get_service_addresses("messages-service")
    logging_addresses = get_service_addresses("logging-service")
    
    print(f"Found message services: {messages_addresses}")
    print(f"Found logging services: {logging_addresses}")
    
    messages_data = get_service_data(messages_addresses, "/messages")
    logs_data = get_service_data(logging_addresses, "/logs", first_random=True)
    

    return {
        "status":"success",
        "data":{
            "msg_clusters": [len(messages_addresses)],
            "messages": messages_data,
            "logs": logs_data
        }
    }


@app.post("/", status_code=201)
def post_facade(message: Message):
    content = message.msg
    id = str(uuid.uuid4())
    logging_addresses = get_service_addresses("logging-service")
    
    # Produce message to Kafka
    try:
        producer.produce(topic, content.encode('utf-8'))
        print(f"Produced message to Kafka: {content}")
        producer.flush()
    except Exception as e:
        print(f"Error producing to Kafka: {e}")
    
    # Send to logging service
    log_sent = False
    if logging_addresses:
        random.shuffle(logging_addresses)
        for service_addr in logging_addresses:
            try:
                endpoint = f"{service_addr}/logs"
                print(f"Sending log to: {endpoint}")
                response = requests.post(
                    endpoint, 
                    json={"id": id, "content": content},
                    timeout=3
                )
                if response.status_code == 201:
                    log_sent = True
                    print(f"Successfully logged to {endpoint}")
                    break
            except Exception as e:
                print(f"Failed to send log to {service_addr}: {e}")
    
    if not log_sent:
        print("Warning: Failed to send log to any logging service")

    return {
        "status":"success",
        "data":{
            "id": id,
            "content": content
        }
    }

if __name__ == "__main__":
    print(f"Topic: {topic}")
    print(f"Bootstrap: {bootstrap}")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)