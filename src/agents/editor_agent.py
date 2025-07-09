from src.services.monitoring_service import MonitoringService
from src.services.file_service import FileService
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip
import os


class EditorAgent:
    def __init__(self, session_id):
        self.session_id = session_id
        self.monitoring_service = MonitoringService(self.session_id)
        self.file_service = FileService(self.session_id)

    def edit_video(self, video_clips, audio_track):
        self.monitoring_service.log("EditorAgent: Editing final video.")

        try:
            # Create video clip objects
            clips = [VideoFileClip(clip) for clip in video_clips]
            final_clip = concatenate_videoclips(clips)

            # Add audio track
            if audio_track and os.path.exists(audio_track):
                audioclip = AudioFileClip(audio_track)
                final_clip.audio = audioclip

            # Write the final video file
            final_video_path = os.path.join(self.file_service.session_path, "final_video.mp4")
            final_clip.write_videofile(final_video_path, codec="libx264", audio_codec="aac")

            self.monitoring_service.log(f"EditorAgent: Final video saved to {final_video_path}")
            return final_video_path

        except Exception as e:
            self.monitoring_service.log(f"EditorAgent: Error editing video: {e}")
            return None

