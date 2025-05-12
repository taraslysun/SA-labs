import hazelcast
import uvicorn
import os
from pydantic import BaseModel
from fastapi import FastAPI
from contextlib import asynccontextmanager
from hz_node import start_hz_node
import os
import consul
import json

CONSUL_HOST = os.getenv("CONSUL_HOST", "localhost")
CONSUL_PORT = int(os.getenv("CONSUL_PORT", "8500"))
consul_client = consul.Consul(host=CONSUL_HOST, port=CONSUL_PORT)
SERVICE_NAME = os.getenv("SERVICE_NAME", "logging-service")
SERVICE_ID   = f"{SERVICE_NAME}-{os.getenv('HOSTNAME')}"
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8001"))

class LoggedMessage(BaseModel):
    id:str
    content:str


hz_ip = os.getenv("HZ_IP", "0.0.0.0")
hz_port = int(os.getenv("HZ_PORT", "5701"))

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    consul_client.agent.service.register(
        name=SERVICE_NAME,
        service_id=SERVICE_ID,
        address=os.getenv("HOSTNAME"),
        port=SERVICE_PORT,
        check=consul.Check.http(
                url=f"http://{os.getenv("HOSTNAME")}:{SERVICE_PORT}/health",
                interval="10s"
            )
        )
    try:
        yield
    finally:
        hz_container.stop()
        hz_container.remove()
        print("Hazelcast container stopped and removed")
        client.shutdown()
        consul_client.agent.service.deregister(SERVICE_ID)


@app.get("/health")
def health():
    return {"status": "healthy"}


app.router.lifespan_context = lifespan

hz_container = start_hz_node(hz_ip, hz_port)
index, data = consul_client.kv.get('hazelcast/cluster_members')
members = json.loads(data['Value'].decode())
client = hazelcast.HazelcastClient(cluster_name='logs-db', cluster_members=members)

# client = hazelcast.HazelcastClient(
#     cluster_name='logs-db', 
#     cluster_members=[f'{hz_ip}:{hz_port}']
# )

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
    

if __name__ == '__main__':
    
    uvicorn.run(app, host='0.0.0.0', port=8001)
