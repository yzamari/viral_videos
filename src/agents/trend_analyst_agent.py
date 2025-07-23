from src.services.monitoring_service import MonitoringService
from src.services.file_service import FileService
from config.config import settings
from googleapiclient.discovery import build

class TrendAnalystAgent:
    def __init__(self, session_id):
        self.session_id = session_id
        self.monitoring_service = MonitoringService(self.session_id)
        self.file_service = FileService(self.session_id)
        self.youtube = self._get_youtube_service()

    def _get_youtube_service(self):
        if settings.youtube_api_key:
            return build("youtube", "v3", developerKey=settings.youtube_api_key)
        return None

    def analyze(self, topic):
        self.monitoring_service.log(f"TrendAnalystAgent: Analyzing trends for topic - {topic}")
        
        if self.youtube:
            self.monitoring_service.log(f"TrendAnalystAgent: Performing topic search on YouTube for '{topic}'.")
            try:
                # Search for videos related to the topic
                search_request = self.youtube.search().list(
                    q=topic,
                    part="snippet",
                    type="video",
                    order="viewCount",
                    maxResults=10
                )
                search_response = search_request.execute()

                video_ids = [item['id']['videoId'] for item in search_response.get(
                    "items",
                    [])]

                if not video_ids:
                    self.monitoring_service.log(
                        f"TrendAnalystAgent: No videos found for topic '{topic}'. Using mock data.")
                    return self._get_mock_data(topic)

                # Get details for the found videos
                video_request = self.youtube.videos().list(
                    part="snippet,contentDetails,statistics",
                    id=",".join(video_ids)
                )
                video_response = video_request.execute()

                trends = {
                    "topic": topic,
                    "youtube_trending": video_response.get(
                        "items",
                        []),
                    "source": "YouTube Search"}
            except Exception as e:
                self.monitoring_service.log(f"TrendAnalystAgent: Error fetching from YouTube API: {e}")
                trends = self._get_mock_data(topic)
        else:
            self.monitoring_service.log("TrendAnalystAgent: YouTube API key not found. Using mock data.")
            trends = self._get_mock_data(topic)

        self.file_service.save_json("trend_analysis.json", trends)
        self.monitoring_service.log("TrendAnalystAgent: Trend analysis complete.")
        return trends

    def _get_mock_data(self, topic):
        return {"topic": topic, "related_keywords": ["viral", "video", "trends"], "source": "Mock Data"}
