## Lab 4: Microservices with Hazelcast

Author: Taras Lysun

### Description
This lab was about further implementing the microservices architecture. The task was to add message queue in order to work with message services.

### Prerequisites
- Docker
- Docker Compose
- Python 3.12
- FastAPI

### How to run

Pull the repository
```bash
git clone https://github.com/taraslysun/SA-labs
git switch micro_mq
cd SA-labs
```

Make virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

Install requirements
```bash
pip install -r requirements.txt
```

Launch application

**In the ```compose.yaml``` file don't forget the HZ_IP varibles. Set your IP in order for the containers to communicate with each other. You can find your IP by running:**
```bash
hostname -I | awk '{print $1}'
```

Then run the following command to start the application:
```bash
# if the logging service is not working, change the address to your local ip in the compose.sh
docker compose up --build
```
or (linux-only)
```bash
./launch_servers.sh
```

After setting everything up, you can fill the application either by curl:
```bash
curl -X POST http://localhost:8000/ -H "Content-Type: application/json" -d '{"msg": "Hello, world!"}'
```
or with 100 messages by running the following command:
```bash
python3 fill_system.py
```

And then check the whole system by running the following command:
```bash
curl -X GET http://localhost:8000/
```
