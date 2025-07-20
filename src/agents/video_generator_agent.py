from src.services.monitoring_service import MonitoringService
from src.services.file_service import FileService
from src.generators.video_generator import VideoGenerator
from config.config import settings
import uuid
import os

class VideoGeneratorAgent:
    def __init__(self, session_id):
        self.session_id = session_id
        self.monitoring_service = MonitoringService(self.session_id)
        self.file_service = FileService(self.session_id)
        
        # Initialize video generator
        self.video_generator = VideoGenerator(
            api_key=settings.google_api_key,
            use_real_veo2=True,
            use_vertex_ai=True,
            vertex_project_id=settings.veo_project_id,
            vertex_location=settings.veo_location,
            vertex_gcs_bucket=os.getenv('VERTEX_AI_GCS_BUCKET', 'viral-veo2-results'),
            output_dir="outputs"
        )

    def generate_clips(self, storyboard):
        self.monitoring_service.log("VideoGeneratorAgent: Generating video clips.")

        video_clips = []
        video_id = str(uuid.uuid4())

        prompts = [scene["description"] for scene in storyboard["scenes"]]

        generated_clips = self.video_generator.generate_batch_clips(
            prompts=[{"description": p} for p in prompts],
            config={"duration_seconds": 15, "platform": "youtube"},
            video_id=video_id
        )

        for clip_info in generated_clips:
            video_clips.append(clip_info['clip_path'])

        self.file_service.save_json("video_clips.json", {"clips": video_clips})
        self.monitoring_service.log("VideoGeneratorAgent: Video clip generation complete.")
        return video_clips
