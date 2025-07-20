import os
from datetime import datetime

class MonitoringService:
    def __init__(self, session_id):
        # Fix path construction to match actual session directory format
        if session_id.startswith("session_"):
            session_dir = os.path.join("outputs", session_id)
        else:
            session_dir = os.path.join("outputs", f"session_{session_id}")

        # Ensure the directory exists
        os.makedirs(session_dir, exist_ok=True)

        self.log_file = os.path.join(session_dir, "generation_log.txt")

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"

        # Ensure directory exists before writing
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

        with open(self.log_file, "a") as f:
            f.write(log_message)
        print(log_message)
