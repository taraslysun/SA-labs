FROM python:3.12-slim

WORKDIR /app

RUN pip install docker uvicorn fastapi requests hazelcast-python-client 


COPY . . 

EXPOSE 8001

CMD [ "python3", "logging-service.py" ]