FROM python:3.12-slim

WORKDIR /app

RUN pip install uvicorn fastapi requests

COPY . .

EXPOSE 8007

CMD [ "python3", "messages-service.py" ]