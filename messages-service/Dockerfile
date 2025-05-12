FROM python:3.12-slim

WORKDIR /app

RUN pip install uvicorn fastapi requests confluent-kafka python-consul

COPY . .

EXPOSE 8005

CMD [ "python3", "messages-service.py" ]