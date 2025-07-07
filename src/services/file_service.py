import os
import json
from datetime import datetime


class FileService:
    def __init__(self, session_id):
        self.session_id = session_id
        self.session_path = os.path.join("outputs", self.session_id)
        os.makedirs(self.session_path, exist_ok=True)

    @staticmethod
    def create_session_folder():
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(os.path.join("outputs", session_id), exist_ok=True)
        return session_id

    def save_json(self, filename, data):
        with open(os.path.join(self.session_path, filename), "w") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def save_video(session_id, video_data):
        # Placeholder for saving video data
        video_path = os.path.join("outputs", session_id, "final_video.mp4")
        with open(video_path, "w") as f:
            f.write("video data")
        return video_path 