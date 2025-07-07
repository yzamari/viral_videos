from src.services.monitoring_service import MonitoringService
from src.services.file_service import FileService


class DirectorAgent:
    def __init__(self, session_id):
        self.session_id = session_id
        self.monitoring_service = MonitoringService(self.session_id)
        self.file_service = FileService(self.session_id)

    def create_storyboard(self, script):
        self.monitoring_service.log("DirectorAgent: Creating storyboard.")
        # Placeholder for storyboard creation logic
        storyboard = {
            "title": script["title"],
            "scenes": [
                {**scene, "visuals": f"Visuals for scene {scene['scene']}"}
                for scene in script["scenes"]
            ],
        }
        self.file_service.save_json("storyboard.json", storyboard)
        self.monitoring_service.log("DirectorAgent: Storyboard creation complete.")
        return storyboard 