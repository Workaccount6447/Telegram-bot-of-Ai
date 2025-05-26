# fake_server.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "Bot is running"}
