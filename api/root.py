import logging
logging.basicConfig(level=logging.INFO)
from api import app

@app.get("/")
async def root_endpoint():
    return {"message": "Serverless function is alive. 💪"}