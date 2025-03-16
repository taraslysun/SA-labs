## Lab 3: Microservices with Hazelcast

Author: Taras Lysun

### Description
This lab was about further implementing the microservices architecture. The task was to add possibility for multiple nodes of logging service.

### Prerequisites
- Docker
- Docker Compose
- Python 3.12
- FastAPI

### How to run
```bash
git clone https://github.com/taraslysun/SA-labs
cd SA-labs
git checkout micro_hazelcast
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
```bash
docker-compose up --build
```
or (linux-only)
```bash
./launch_servers.sh
```
