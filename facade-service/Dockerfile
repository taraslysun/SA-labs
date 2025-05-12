FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install uvicorn fastapi requests confluent-kafka python-consul

EXPOSE 8000

CMD ["python3", "facade-service.py"]