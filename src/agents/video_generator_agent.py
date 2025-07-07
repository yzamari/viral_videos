from src.services.monitoring_service import MonitoringService
from src.services.file_service import FileService
from src.generators.smart_veo2_client import SmartVeo2Client
from config.config import settings
import uuid


class VideoGeneratorAgent:
    def __init__(self, session_id):
        self.session_id = session_id
        self.monitoring_service = MonitoringService(self.session_id)
        self.file_service = FileService(self.session_id)
        self.video_client = SmartVeo2Client(
            api_key=settings.google_api_key,
            output_dir=self.file_service.session_path
        )

    def generate_clips(self, storyboard):
        self.monitoring_service.log("VideoGeneratorAgent: Generating video clips.")
        
        video_clips = []
        video_id = str(uuid.uuid4())
        
        prompts = [scene["description"] for scene in storyboard["scenes"]]
        
        generated_clips = self.video_client.generate_batch_clips(
            prompts=[{"description": p} for p in prompts],
            config={"duration_seconds": 15, "platform": "youtube"},
            video_id=video_id
        )

        for clip_info in generated_clips:
            video_clips.append(clip_info['clip_path'])

        self.file_service.save_json("video_clips.json", {"clips": video_clips})
        self.monitoring_service.log("VideoGeneratorAgent: Video clip generation complete.")
        return video_clips 