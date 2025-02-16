import fastapi


app = fastapi.FastAPI()


@app.get("/")
def get_messages():
    return "message service placeholder"