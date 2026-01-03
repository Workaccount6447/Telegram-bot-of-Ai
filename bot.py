import time
import requests
from datetime import datetime

# Links to hit
links = [
    "https://example.com",
    "https://google.com",
    "https://github.com"
]

INTERVAL = 60   # 60 seconds
TIMEOUT = 4     # 4 seconds

print("Started auto requester...\n")

while True:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Run time: {current_time}")

    for link in links:
        try:
            response = requests.get(link, timeout=TIMEOUT)
            print(f"[{current_time}] {link} → {response.status_code}")
        except requests.RequestException as e:
            print(f"[{current_time}] {link} → ERROR: {e}")

    print("Waiting 60 seconds...\n")
    time.sleep(INTERVAL)
