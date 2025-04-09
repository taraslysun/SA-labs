FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install dotenv uvicorn fastapi

EXPOSE 8008

CMD [ "python3", "config-server.py" ]