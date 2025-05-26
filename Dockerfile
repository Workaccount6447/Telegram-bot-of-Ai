FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Expose a dummy port for Koyeb
EXPOSE 7860

# Run both the bot and the fake HTTP server
CMD ["sh", "-c", "uvicorn fake_server:app --host 0.0.0.0 --port 7860 & python telegram_bot_env_ready.py"]
