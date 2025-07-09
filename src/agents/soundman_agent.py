from src.services.monitoring_service import MonitoringService
from src.services.file_service import FileService
from gtts import gTTS
import os


class SoundmanAgent:
    def __init__(self, session_id):
        self.session_id = session_id
        self.monitoring_service = MonitoringService(self.session_id)
        self.file_service = FileService(self.session_id)

    def generate_audio(self, script):
        self.monitoring_service.log("SoundmanAgent: Generating audio track.")

        text_to_speak = ". ".join([scene["description"] for scene in script["scenes"]])

        try:
            tts = gTTS(text=text_to_speak, lang='en')
            audio_path = os.path.join(self.file_service.session_path, "audio.mp3")
            tts.save(audio_path)
            self.monitoring_service.log(f"SoundmanAgent: Audio track saved to {audio_path}")
            return audio_path
        except Exception as e:
            self.monitoring_service.log(f"SoundmanAgent: Error generating audio: {e}")
            return None

