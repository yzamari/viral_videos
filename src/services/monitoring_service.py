import os
from datetime import datetime


class MonitoringService:
    def __init__(self, session_id):
        self.log_file = os.path.join("outputs", session_id, "generation_log.txt")

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        with open(self.log_file, "a") as f:
            f.write(log_message)
        print(log_message) 