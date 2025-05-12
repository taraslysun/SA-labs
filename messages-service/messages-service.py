import fastapi
import uvicorn
from confluent_kafka import Consumer
from contextlib import asynccontextmanager
import threading
import os
import consul
from consul import Check

CONSUL_HOST = os.getenv("CONSUL_HOST", "localhost")
CONSUL_PORT = int(os.getenv("CONSUL_PORT", "8500"))
consul_client = consul.Consul(host=CONSUL_HOST, port=CONSUL_PORT)
SERVICE_NAME = os.getenv("SERVICE_NAME", "messages-service")
SERVICE_ID   = f"{SERVICE_NAME}-{os.getenv('HOSTNAME')}"
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8005"))

app = fastapi.FastAPI()

_, bs_data = consul_client.kv.get('mq/bootstrap_servers')
bootstrap = bs_data['Value'].decode()
_, topic_data = consul_client.kv.get('mq/topic')
topic = topic_data['Value'].decode()

consumer = Consumer({'bootstrap.servers': bootstrap, 'group.id': SERVICE_NAME, 'auto.offset.reset': 'earliest'})
consumer.subscribe([topic])

def kafka_consumer_loop():
    i = 0
    while True:
        msg = consumer.poll(1.0)
        i += 1  
        if msg is None:
            continue
        if msg.error():
            print(f"Error: {msg.error()}")
            continue
        decoded = msg.value().decode('utf-8')
        messages.append(decoded)
        print(f"Received message: {decoded}")

messages = []

@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    hostname = os.getenv("HOSTNAME", "localhost")
    print(f"Registering service {SERVICE_NAME} with ID {SERVICE_ID} at {hostname}:{SERVICE_PORT}")
    
    consul_client.agent.service.register(
        name=SERVICE_NAME,
        service_id=SERVICE_ID,
        address=hostname,
        port=SERVICE_PORT,
        check=Check.http(
            url=f"http://{hostname}:{SERVICE_PORT}/health",
            interval="10s"
        )
    )
    try:
        yield
    finally:
        consumer.close()
        print("Kafka consumer closed")
        consul_client.agent.service.deregister(SERVICE_ID)

app.router.lifespan_context = lifespan

@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/messages", status_code=200)
def get_messages() -> dict:
    return {
        "status":"success",
        "data": messages
    }

@app.delete("/messages", status_code=200)
def delete_messages() -> dict:
    global messages
    messages = []
    return {
        "status":"success",
        "data": messages
    }

@app.get("/", status_code=200)
def root():
    """Root endpoint for service discovery checks"""
    return get_messages()

if __name__ == '__main__':
    thread = threading.Thread(target=kafka_consumer_loop, daemon=True)
    thread.start()
    print(f"Bootstrap servers: {bootstrap}")
    print(f"Topic: {topic}")

    uvicorn.run(app, host='0.0.0.0', port=8005)