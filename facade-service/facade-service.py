import fastapi
import requests
import uuid

messages_address = "http://localhost:8001"
loggings_address = "http://localhost:8002"

app = fastapi.FastAPI()

@app.get("/")
def get_facade():
    response_messages = requests.get(messages_address)
    response_loggings = requests.get(loggings_address)
    return {
        "messages": response_messages.json(),
        "loggings": response_loggings.json()
    }


@app.post("/")
def post_facade(message: dict):
    message_content = message.get("msg")
    message_id = str(uuid.uuid4())
    requests.post(loggings_address, json={message_id: message_content})
    return 200