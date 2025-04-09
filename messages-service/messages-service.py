import fastapi
import uvicorn
from confluent_kafka import Consumer
from contextlib import asynccontextmanager
import threading

app = fastapi.FastAPI()

conf = {
    'bootstrap.servers': 'kafka-1:9092,kafka-2:9092,kafka-3:9092',
    'group.id': 'messages-service',
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(**conf)
consumer.subscribe(['messages'])

def kafka_consumer_loop():
    i = 0
    while True:
        msg = consumer.poll(1.0)
        print("Polling for messages...", i)
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
    try:
        yield
    finally:
        consumer.close()
        print("Kafka consumer closed")



@app.get("/messages", status_code=200)
def get_messages() -> dict:
    return {
        "status":"success",
        "data": messages
    }

if __name__ == '__main__':
    thread = threading.Thread(target=kafka_consumer_loop, daemon=True)
    thread.start()
    uvicorn.run(app, host='0.0.0.0', port=8005)