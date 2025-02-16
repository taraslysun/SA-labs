import fastapi


app = fastapi.FastAPI()

table = {}

@app.post('/')
def save_message(message: dict):
    print(message)
    message_id, message_content = list(message.items())[0]
    table[message_id] = message_content
    return {message_id: message_content}

@app.get('/')
def get_messages():
    return ', '.join(list(table.values()))