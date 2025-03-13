import fastapi
import uvicorn

app = fastapi.FastAPI()

@app.get("/messages", status_code=200)
def get_messages() -> dict:
    return {
        "status":"success",
        "data":"message service placeholder"
    }

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8007)