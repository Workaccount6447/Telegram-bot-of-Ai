# Use Python image
FROM python:3.11-slim

# Set working dir
WORKDIR /app

# Install system deps (ffmpeg for yt-dlp)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Copy files
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run the bot
CMD ["python", "bot.py"]
