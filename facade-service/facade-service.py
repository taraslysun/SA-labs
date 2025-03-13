import fastapi
import requests
import uuid
from pydantic import BaseModel
import random


CONFIG_ADDRESS = "http://config-server:8008/services"

app = fastapi.FastAPI()

class Message(BaseModel):
    msg:str


def get_service_addresses(service_name: str) -> list:
    try:
        response = requests.get(CONFIG_ADDRESS, json={"name": service_name})
        return response.json().get("data", [])
    except Exception as e:
        print(f"Exception in {service_name}: {e}")
        return []


def get_service_data(addresses: list) -> dict:
    random.shuffle(addresses)
    for service_addr in addresses:
        try:
            response = requests.get(service_addr)
            return response.json().get("data", {})
        except Exception as e:
            print(f"Exception in {service_addr}: {e}")
    return {"error": "Could not connect to service"}


@app.get("/", status_code=200)
def get_facade():
    messages_addresses = get_service_addresses("messages-service")
    logging_addresses = get_service_addresses("logging-service")
    
    messages_data = get_service_data(messages_addresses)
    logs_data = get_service_data(logging_addresses)

    return {
        "status":"success",
        "data":{
            "messages": messages_data,
            "logs": logs_data
        }
    }


@app.post("/", status_code=201)
def post_facade(message: Message):
    content = message.msg
    id = str(uuid.uuid4())
    logging_addresses = get_service_addresses("logging-service")

        
    random.shuffle(logging_addresses)
    for service_addr in logging_addresses:
        try:
            requests.post(service_addr, json={"id": id, "content": content})
            break
        except Exception as e:
            print(e)

    return {
        "status":"success",
        "data":{
            "id":id,
            "content":content
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)