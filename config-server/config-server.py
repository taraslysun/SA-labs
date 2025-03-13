from fastapi import FastAPI
from pydantic import BaseModel
import os
from dotenv import load_dotenv

app = FastAPI()

load_dotenv()


class ServiceName(BaseModel):
    name: str


SERVICES = {
    "logging-service" : (os.getenv("LOGGING_ADDRESSES") or "").split(';'),
    "messages-service" : (os.getenv("MESSAGES_ADDRESSES") or "").split(';')
}

@app.get("/services", status_code=200)
def get_service(service_name: ServiceName) -> dict:
    if service_name.name not in SERVICES:
        return {
            "status":"error",
            "data":"Service not found"
        }

    return {
        "status":"success",
        "data":SERVICES[service_name.name]
    }

if __name__=="__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)