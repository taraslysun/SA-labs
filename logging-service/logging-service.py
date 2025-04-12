import hazelcast
import uvicorn
import os
from pydantic import BaseModel
from fastapi import FastAPI
from contextlib import asynccontextmanager
from hz_node import start_hz_node

class LoggedMessage(BaseModel):
    id:str
    content:str


def start_logging_service(hz_ip, hz_port: int) -> FastAPI:
    app = FastAPI()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        try:
            yield
        finally:
            hz_container.stop()
            hz_container.remove()
            print("Hazelcast container stopped and removed")
            client.shutdown()

    app.router.lifespan_context = lifespan

    hz_container = start_hz_node(hz_ip, hz_port)
    client = hazelcast.HazelcastClient(
        cluster_name='logs-db', 
        cluster_members=[f'{hz_ip}:{hz_port}']
    )

    table = client.get_map('logs-map')

    @app.post("/logs", status_code=201)
    async def save_message(message: LoggedMessage) -> dict:
        table.put(message.id, message.content)
        print(f"Saved message: {message.id} - {message.content}")
        return {
            "status":"success",
            "data":{
                "id":message.id,
                "content":message.content
            }
        }

    @app.get("/logs", status_code=200)
    async def get_messages() -> dict:
        logs = table.values().result()
        return {
            "status":"success",
            "data":','.join(logs)
        }
    
    @app.delete("/logs", status_code=200)
    async def delete_messages() -> dict:
        table.clear()
        return {
            "status":"success",
            "data":"Logs deleted"
        }
    
    return app


if __name__ == '__main__':
    hz_ip = os.getenv("HZ_IP", "0.0.0.0")
    hz_port = int(os.getenv("HZ_PORT", "5701"))

    app = start_logging_service(hz_ip, hz_port)
    
    uvicorn.run(app, host='0.0.0.0', port=8001)
